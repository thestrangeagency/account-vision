# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-08-17 11:05
from __future__ import unicode_literals

from django.db import migrations, models


def forward(apps, schema_editor):
    AvUser = apps.get_model('av_account', 'AvUser')
    for user in AvUser.objects.all().iterator():
        user.is_2fa = user.is_verified
        user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('av_account', '0012_communications_trial_change_notice'),
    ]

    operations = [
        migrations.AddField(
            model_name='avuser',
            name='is_2fa',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(forward),
    ]
