# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-08-16 14:44
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('groupaccount', '0002_auto_20150609_2202'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='groupaccount',
            name='number',
        ),
    ]