# Generated by Django 3.2.8 on 2021-11-05 20:34

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_client_notification_status'),
        ('swipe', '0009_alter_announcement_flat'),
    ]

    operations = [
        migrations.AddField(
            model_name='housenews',
            name='publication_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='developerhouse',
            unique_together={('developer', 'house')},
        ),
    ]
