# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-10-25 12:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coffee', '0011_coffee_for_sale'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='archived',
            field=models.BooleanField(default=False),
        ),
    ]
