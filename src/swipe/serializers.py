import logging

from django.core import validators
from django.db.models import fields
from rest_framework import serializers

from swipe.models import AnnouncementImage, House, Announcement, Flat, HouseImage, HouseNews, DeveloperHouse, Promotion, ClientAnnouncementFavourites, ClientHouseFavourites

logger = logging.getLogger(__name__)

class HouseNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseNews
        fields = '__all__'


class HouseImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseImage
        exclude = 'house',


class HouseListSerializer(serializers.HyperlinkedModelSerializer):
    detail_url = serializers.HyperlinkedIdentityField(
        view_name='swipe:house-detail'
    )
    address = serializers.SerializerMethodField('get_address')
    from_summ = serializers.SerializerMethodField('get_from_summ')
    from_area = serializers.SerializerMethodField('get_from_area')
    avatar = serializers.SerializerMethodField('get_avatar')

    def get_address(self, house):
        if len(house.flats.all()) and len(house.flats.first().announcements.all()):
            announcements = Announcement.objects.filter(
                flat__in=[flat.pk for flat in house.flats.all()])
            return announcements.first().address
        else:
            return '-'

    def get_from_summ(self, house):
        if len(house.flats.all()) and len(house.flats.first().announcements.all()):
            announcements = Announcement.objects.filter(
                flat__in=[flat.pk for flat in house.flats.all()])
            return min([an.price for an in announcements])
        else:
            return '-'

    def get_from_area(self, house):
        if len(house.flats.all()) and len(house.flats.first().announcements.all()):
            announcements = Announcement.objects.filter(
                flat__in=[flat.pk for flat in house.flats.all()])
            return min([an.total_area for an in announcements])
        else:
            return '-'

    def get_avatar(self, house):
        return '-' if not house.images.all() else house.images.first().image.url

    class Meta:
        model = House
        fields = 'detail_url', 'id', 'name', 'address', 'from_summ', 'from_area', 'avatar'


class HouseSerializer(serializers.HyperlinkedModelSerializer):
    images = HouseImagesSerializer(many=True)

    class Meta:
        model = House
        fields = ('id', 'name', 'description', 'status', 'type', '_class', 'building_technology',
            'territory', 'sea_distance', 'communal_payments', 'ceiling_height', 'has_gas', 
            'heating_type', 'sewerage', 'water_supply', 'water_supply', 'calculation_type',
            'perpose', 'summ_in_contract', 'housings', 'sections', 'floors', 'coords', 'images')

    def validate(self, data):
        user = self.context['request'].user
        if self.partial:
            pass
        else:
            if data['status'] != '2' and user.user_developer is None:
                raise serializers.ValidationError('Только застройщики могут добавлять многоквартирные дома')
            if (data['status'] == '1' and data['type'] not in ['1', '2']):
                raise serializers.ValidationError('Неверный вид дома для выбранного статуса')
        return data

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        house = House.objects.create(**validated_data)
        if self.context['request'].user.user_developer is not None:
            DeveloperHouse.objects.create(house=house,
                developer=self.context['request'].user.user_developer)
        for image in images_data:
            HouseImage.objects.create(house=house, image=image.get('image'))
        return house


class PromotionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Promotion
        exclude = ['id', 'announcement']


class AnnouncementImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnouncementImage
        exclude = 'announcement',


class AnnouncementListSerializer(serializers.HyperlinkedModelSerializer):
    detail_url = serializers.HyperlinkedIdentityField(
        view_name='swipe:announcement-detail'
    )
    flat_detail = serializers.SerializerMethodField('get_flat_detail')
    promotion = PromotionSerializer(read_only=True)
    avatar = serializers.SerializerMethodField('get_avatar')

    def get_flat_detail(self, announcement):
        result = f'{announcement.rooms} квартира, {announcement.total_area} м2'
        if announcement.flat is not None:
            result += f', {announcement.flat.section}/{announcement.flat.floor} эт.'
        return result
    
    def get_avatar(self, announcement):
        return '-' if not announcement.images.all() else announcement.images.first().image.url

    class Meta:
        model = Announcement
        fields = ['detail_url', 'flat_detail', 'id', 'price', 'address', 
            'publication_date', 'promotion', 'avatar']


class AnnouncementRetrieveSerializer(serializers.ModelSerializer):
    images = AnnouncementImagesSerializer(many=True)

    class Meta:
        model = Announcement
        fields = ('id', 'address', 'flat', 'foundation_document', 
            'appointment', 'rooms', 'layout', 'state', 'total_area', 
            'has_balcony', 'calculation_options', 'commision',
            'communication', 'description', 'price', 'advertiser', 'publication_date', 'images')

    def create(self, validated_data):
        images_data = validated_data.pop('images')
        announcement = Announcement.objects.create(**validated_data)
        Promotion.objects.create(announcement=announcement)
        for image in images_data:
            AnnouncementImage.objects.create(announcement=announcement, image=image.get('image'))
        return announcement


class AnnouncementToTheTopSerializer(serializers.ModelSerializer):
    publication_date = serializers.DateTimeField()
    class Meta:
        model = Announcement
        fields = ['publication_date']


class AnnouncementAdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = Announcement
        fields = '__all__'


class AnnoncementFavouritesSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClientAnnouncementFavourites
        fields = ['announcement', 'client']


class AnnoncementFavouritesCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClientAnnouncementFavourites
        fields = []


class HouseFavouritesSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClientHouseFavourites
        fields = ['house']

    def create(self, validated_data):
        favourite = ClientHouseFavourites.objects.create(
            **validated_data, 
            client=self.context['request'].user.user_client)
        return favourite


class FlatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flat
        fields = '__all__'
    
    def validate(self, data):
        if self.partial:
            if 'house' in data and data['house'] != self.instance.house:
                raise serializers.ValidationError('Дом менять нельзя')
            if 'housing' in data and data['housing'] > self.instance.house.housings:
                raise serializers.ValidationError('У дома корпусов меньше')
            if 'section' in data and data['section'] > self.instance.house.sections:
                raise serializers.ValidationError('У дома секций меньше')
            if 'floor' in data and data['floor'] > self.instance.house.floors:
                raise serializers.ValidationError('У дома этажей меньше')
        else:
            if data['housing'] > data['house'].housings:
                raise serializers.ValidationError('У дома корпусов меньше')
            if data['section'] > data['house'].sections:
                raise serializers.ValidationError('У дома секций меньше')
            if data['floor'] > data['house'].floors:
                raise serializers.ValidationError('У дома этажей меньше')
        return data

    def create(self, validated_data):
        flat = Flat.objects.create(**validated_data)
        if self.context['request'].user.user_developer is not None:
            flat.status = True
            flat.save()
        return flat