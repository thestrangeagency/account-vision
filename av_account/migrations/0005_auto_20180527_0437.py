# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-05-27 08:37
from __future__ import unicode_literals

import av_account.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('av_account', '0004_auto_20180522_0509'),
    ]

    operations = [
        migrations.AddField(
            model_name='avuser',
            name='is_paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='avuser',
            name='trial_end',
            field=models.DateTimeField(null=True),
            # had to go back end change this in order to remove trial_end method from model
            # field=models.DateTimeField(default=av_account.models.trial_end),
        ),
    ]
