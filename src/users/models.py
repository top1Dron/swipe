from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from users.managers import UserManager

class User(AbstractUser):
    username = None
    email = models.EmailField('E-mail', unique=True)
    phone_number = models.CharField("Номер телефона", max_length=20, unique=True,
        # valid=[+38(093)1350239,+38(093)135-02-39,+38(093)135 02 39,+380931350239,0931350239,+380445371428, +38(044)5371428,+38(044)537 14 28,+38(044)537-14-28,+38(044) 537.14.28,044.537.14.28,0445371428,044-537-1428,(044)537-1428,044 537-1428]
        # invalid = [+83(044)537 14 28,088 537-1428]
        validators=[
            validators.RegexValidator(
                regex=r'^(?:\+38)?(?:\(0[0-9][0-9]\)[ .-]?[0-9]{3}[ .-]?[0-9]{2}[ .-]?[0-9]{2}|044[ .-]?[0-9]{3}[ .-]?[0-9]{2}[ .-]?[0-9]{2}|0[0-9][0-9][0-9]{7})$')
        ])

    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']

    def __str__(self) -> str:
        return self.email

    @property
    def user_client(self):
        try:
            return self.client
        except:
            return None

    @property
    def user_developer(self):
        try:
            return self.developer
        except:
            return None

    @property
    def user_notary(self):
        try:
            return self.notary
        except:
            return None


class Client(models.Model):
    STATUSES = (
        ('1', 'Мне'),
        ('2', 'Мне и агенту'),
        ('3', 'Агенту'),
        ('4', 'Отключить'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client')
    notification_status = models.CharField(max_length=2, choices=STATUSES, default='4')

    @property
    def client_agent(self):
        try:
            return self.agent
        except:
            return None

    @receiver(post_save, sender = User)
    def create_profile_for_user(sender, instance=None, created=False, **kwargs):
        if created:
            Client.objects.get_or_create(user=instance)


class Agent(models.Model):
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='agent')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField('E-mail', unique=True)
    phone_number = models.CharField("Номер телефона", max_length=20, unique=True,
        validators=[
            validators.RegexValidator(
                regex=r'^(?:\+38)?(?:\(0[0-9][0-9]\)[ .-]?[0-9]{3}[ .-]?[0-9]{2}[ .-]?[0-9]{2}|044[ .-]?[0-9]{3}[ .-]?[0-9]{2}[ .-]?[0-9]{2}|0[0-9][0-9][0-9]{7})$')
        ])


class Developer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='developer')


class Notary(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notary')