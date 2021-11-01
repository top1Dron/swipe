from django.contrib.auth.models import BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, phone_number, password=None):
        """
        Creates and saves a User with the given email, phone
        number and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            phone_number=phone_number,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    
    def create_superuser(self, email, phone_number, password=None):
        """
        Creates and saves a superuser with the given email, phone
        number and password.
        """
        user = self.create_user(
            email,
            password=password,
            phone_number=phone_number,
        )
        user.is_staff = True
        user.is_superuser = True
        user.status = '2'
        user.save(using=self._db)
        return user