# Generated by Django 4.0.3 on 2023-07-17 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0009_watchliststorage'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='is_closed',
            field=models.BooleanField(default=False),
        ),
    ]