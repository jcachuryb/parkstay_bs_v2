# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-08-26 02:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkstay', '0056_booking_property_cache'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='property_cache_version',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
