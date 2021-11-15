from datetime import datetime as dt
from pathlib import Path
import os

from django.core import validators
from django.db import models
from django.dispatch.dispatcher import receiver

from users.models import Client, Notary, Developer


def get_upload_path(instance, filename):
    return filename


class House(models.Model):
    STATUSES = (
        ('1', 'Квартиры'),
        ('2', 'Новострой'),
    )

    TYPES = (
        ('1', 'Многоквартирный'),
        ('2', 'Малоквартирный'),
        ('3', 'С гаражом'),
        ('4', 'Без гаража'),
    )

    CLASSES = (
        ('1', 'Элитный'),
        ('2', 'Бюджетный'),
    )

    TECHNOLOGIES = (
        ('1', 'Монолитный каркас с керамзитом'),
        ('2', 'Кирпич'),
        ('3', 'Панель'),
        ('4', 'Монолитный кирпич'),
    )

    TERRITORIES = (
        ('1', 'Закрытая охраняемая'),
        ('2', 'Закрытая не охраняемая'),
        ('3', 'Открытая'),
    )

    PAYMENTS = (
        ('1', 'Платежи'),
        ('2', 'Взносы'),
        ('3', 'Нету'),
    )

    GAS_STATUSES = (
        ('1', 'Да'),
        ('2', 'Нет'),
    )

    HEATING_TYPES = (
        ('1', 'Центральное'),
        ('2', 'Водяное'),
        ('3', 'Воздушное'),
        ('4', 'Электрическое'),
    )

    SEWERAGES = (
        ('1', 'Центарльная'),
        ('2', 'Промышленная'),
        ('3', 'Автономная'),
    )

    WATTER_SUPPLIES = (
        ('1', 'Централизованное'),
        ('2', 'Автономное'),
    )

    name = models.CharField(max_length=50)
    description = models.TextField()
    status = models.CharField(max_length=2, choices=STATUSES)
    type = models.CharField(max_length=2, choices=TYPES)
    _class = models.CharField(max_length=2, choices=CLASSES)
    building_technology = models.CharField(max_length=2, choices=TECHNOLOGIES)
    territory = models.CharField(max_length=2, choices=TERRITORIES)
    sea_distance = models.FloatField(validators=[validators.MinValueValidator(0.0)])
    communal_payments = models.CharField(max_length=2, choices=PAYMENTS)
    ceiling_height = models.FloatField(validators=[validators.MinValueValidator(0.0)])
    has_gas = models.CharField(max_length=1, choices=GAS_STATUSES)
    heating_type = models.CharField(max_length=2, choices=HEATING_TYPES)
    sewerage = models.CharField(max_length=2, choices=SEWERAGES)
    water_supply = models.CharField(max_length=2, choices=WATTER_SUPPLIES)
    registration = models.CharField(max_length=50)
    calculation_type = models.CharField(max_length=50)
    perpose = models.CharField(max_length=50)
    summ_in_contract = models.CharField(max_length=50)
    housings = models.IntegerField(validators=[validators.MinValueValidator(1)])
    sections = models.IntegerField(validators=[validators.MinValueValidator(1)])
    floors = models.IntegerField(validators=[validators.MinValueValidator(1)])
    coords = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class HouseNews(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='house_news')
    header = models.CharField(max_length=50)
    body = models.TextField()
    publication_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-publication_date']


class DeveloperHouse(models.Model):
    developer = models.ForeignKey(Developer, on_delete=models.CASCADE, related_name='dv_house')
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='dv_house')

    class Meta:
        unique_together = ('developer', 'house')


class Flat(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='flats')
    housing = models.IntegerField(validators=[validators.MinValueValidator(1)])
    section = models.IntegerField(validators=[validators.MinValueValidator(1)])
    floor = models.IntegerField(validators=[validators.MinValueValidator(1)])
    number = models.IntegerField(validators=[validators.MinValueValidator(1)])
    status = models.BooleanField(default=False)
    square_meter_price = models.FloatField(validators=[validators.MinValueValidator(0.0)], default=0.0)


class Announcement(models.Model):
    DOCUMENTS = (
        ('1', 'Собственность'),
        ('2', 'Договор с Застройщиком'),
        ('3', 'Договор купли-продажи'),
        ('4', 'Договор купли-продажи и ипотеки'),
    )

    APPOINTMENTS = (
        ('1', 'Апартаменты'),
        ('2', 'Квартира'),
        ('3', 'Дом'),
    )

    ROOMS = (
        ('1', '1 комнатная'),
        ('2', '2 комнатная'),
        ('3', '3 комнатная'),
        ('4', '4 комнатная'),
        ('5', '5 комнатная'),
    )

    LAYOUTS = (
        ('1', 'Студия, санузел'),
        ('2', 'Гостинка'),
        ('3', 'Малосемейка'),
        ('4', 'Изолированные комнаты'),
        ('5', 'Смежные комнаты'),
        ('6', 'Свободная планировка'),
    )

    STATES = (
        ('1', 'Требует ремонта'),
        ('2', 'Не требует ремонта'),
    )
    
    BALCONY_STATES = (
        ('1', 'Есть'),
        ('2', 'Нету'),
    )

    OPTIONS = (
        ('1', 'Наличные'),
        ('2', 'Безнал'),
        ('3', 'Ипотека'),
    )

    MODERATION_STATUSES = (
        ('1', 'Отпралено на проверку'),
        ('2', 'Прошло проверку'),
        ('3', 'Не прошло проверку'),
    )

    AVAILABILITY = (
        ('1', 'Доступно'),
        ('2', 'Не доступно'),
    )

    address = models.CharField(max_length=50)
    flat = models.ForeignKey(Flat, on_delete=models.CASCADE, related_name='announcements', null=True)
    publication_date = models.DateTimeField(auto_now_add=True)
    foundation_document = models.CharField(max_length=2, choices=DOCUMENTS)
    appointment = models.CharField(max_length=2, choices=APPOINTMENTS)
    rooms = models.CharField(max_length=2, choices=ROOMS)
    layout = models.CharField(max_length=2, choices=LAYOUTS)
    state = models.CharField(max_length=2, choices=STATES)
    total_area = models.FloatField(validators=[validators.MinValueValidator(0.0)])
    has_balcony = models.CharField(max_length=2, choices=BALCONY_STATES)
    calculation_options = models.CharField(max_length=2, choices=OPTIONS)
    commision = models.FloatField(validators=[validators.MinValueValidator(0.0)])
    communication = models.CharField(max_length=50)
    description = models.TextField()
    price = models.FloatField(validators=[validators.MinValueValidator(0.0)])
    moder_status = models.CharField(max_length=2, choices=MODERATION_STATUSES, default='1')
    available_status = models.CharField(max_length=2, choices=AVAILABILITY, default='1')
    advertiser = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='announcements')


class AnnouncementImage(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=get_upload_path)


class HouseImage(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=get_upload_path)


class ClientAnnouncementFavourites(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='client_favourites')
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('client', 'announcement')


class ClientHouseFavourites(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='client_house_favourites')
    house = models.ForeignKey(House, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('client', 'house')


class Promotion(models.Model):
    PHRASES = (
        ('0', ''),
        ('1', 'Подарок при покупке'),
        ('2', 'Возможен торг'),
        ('3', 'Квартира у моря'),
        ('4', 'В спальном районе'),
        ('5', 'Вам повезло с ценой!'),
        ('6', 'Для большой семьи'),
        ('7', 'Семейное гнездышко'),
        ('8', 'Отдельная парковка'),
    )

    COLORS = (
        ('0', ''),
        ('1', 'RED'),
        ('2', 'GREEN')
    )

    announcement = models.OneToOneField(Announcement, on_delete=models.CASCADE, related_name='promotion')
    phrase = models.CharField(max_length=2, choices=PHRASES, default='0')
    color = models.CharField(max_length=2, choices=COLORS, default='0')
    is_turbo = models.BooleanField(default=False)
    is_big = models.BooleanField(default=False)


image_attributes = ('image',)


@receiver(models.signals.post_delete, sender=AnnouncementImage)
@receiver(models.signals.post_delete, sender=HouseImage)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding sender object is deleted.
    """
    for attribute in image_attributes:
        if hasattr(instance, attribute):
            attr = getattr(instance, attribute)
            if attr:
                try:
                    if os.path.isfile(attr.path):
                        os.remove(attr.path)
                except ValueError:
                    pass

@receiver(models.signals.post_delete, sender=AnnouncementImage)
@receiver(models.signals.post_delete, sender=HouseImage)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding sender object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        sender_obj = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return False
    old_file = new_file = None
    for attribute in image_attributes:
        if hasattr(sender_obj, attribute):
            old_file = getattr(sender_obj, attribute)
        if hasattr(instance, attribute):
            new_file = getattr(instance, attribute)

    if not old_file == new_file:
        try:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
        except ValueError as e:
            pass