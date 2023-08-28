# Generated by Django 4.2.3 on 2023-08-02 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0017_category_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='auction',
        ),
        migrations.AddField(
            model_name='category',
            name='auction',
            field=models.ManyToManyField(related_name='categories', to='auctions.auction'),
        ),
    ]