from django.core import validators
from django.db.models import fields
from rest_framework import serializers

from swipe.models import House, Announcement, Flat, HouseNews, DeveloperHouse, Promotion, ClientAnnouncementFavourites, ClientHouseFavourites


class HouseNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseNews
        fields = '__all__'


class HouseSerializer(serializers.ModelSerializer):

    class Meta:
        model = House
        fields = ('name', 'description', 'status', 'type', '_class', 'building_technology',
            'territory', 'sea_distance', 'communal_payments', 'ceiling_height', 'has_gas', 
            'heating_type', 'sewerage', 'water_supply', 'water_supply', 'calculation_type',
            'perpose', 'summ_in_contract', 'housings', 'sections', 'floors', 'coords')

    def validate(self, data):
        user = self.context['request'].user
        if self.partial:
            pass
        else:
            if data['status'] != '2' and user.user_developer is None:
                raise serializers.ValidationError('Только застройщики могут добавлять многоквартирные дома')
            if (data['status'] == '1' and data['type'] not in ['1', '2'] or
                data['status'] == '2' and data['type'] not in ['3', '4']):
                raise serializers.ValidationError('Неверный вид дома для выбранного статуса')
        return data

    def create(self, validated_data):
        house = House.objects.create(**validated_data)
        if self.context['request'].user.user_developer is not None:
            DeveloperHouse.objects.create(house=house,
                developer=self.context['request'].user.user_developer)
        return house


class AnnouncementSerializer(serializers.ModelSerializer):

    class Meta:
        model = Announcement
        fields = ('address', 'flat', 'foundation_document', 
            'appointment', 'rooms', 'layout', 'state', 'total_area', 
            'has_balcony', 'calculation_options', 'commision',
            'communication', 'description', 'price')

    def create(self, validated_data):
        announcement = Announcement.objects.create(**validated_data)
        Promotion.objects.create(announcement=announcement)
        return announcement


class AnnoncementFavouritesSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClientAnnouncementFavourites
        fields = ['announcement']

    def create(self, validated_data):
        favourite = ClientAnnouncementFavourites.objects.create(
            **validated_data, 
            client=self.context['request'].user.user_client)
        return favourite


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
            pass
        else:
            if data['housing'] > data['house'].housings:
                raise serializers.ValidationError('У дома корпусов меньше')
            if data['section'] > data['house'].sections:
                raise serializers.ValidationError('У дома секций меньше')
            if data['floor'] > data['house'].floors:
                raise serializers.ValidationError('У дома этажей меньше')
            if data['housing'] > data['house'].housings:
                raise serializers.ValidationError('У дома корпусов меньше')
        return data

    def create(self, validated_data):
        flat = Flat.objects.create(**validated_data)
        if self.context['request'].user.user_developer is not None:
            flat.status = True
            flat.save()
        return flat