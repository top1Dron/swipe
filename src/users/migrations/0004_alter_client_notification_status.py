# Generated by Django 3.2.8 on 2021-10-20 10:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_remove_user_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='notification_status',
            field=models.CharField(choices=[('1', 'Мне'), ('2', 'Мне и агенту'), ('3', 'Агенту'), ('4', 'Отключить')], default='4', max_length=2),
        ),
    ]
