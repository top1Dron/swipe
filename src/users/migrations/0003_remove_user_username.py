# Generated by Django 3.2.8 on 2021-10-18 18:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_managers'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='username',
        ),
    ]
