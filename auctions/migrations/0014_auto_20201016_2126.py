# Generated by Django 3.1.2 on 2020-10-17 03:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0013_bid_winner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='url',
            field=models.CharField(blank=True, max_length=256),
        ),
    ]
