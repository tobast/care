# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
from django.conf import settings


def createDefaultIntervals(apps, schema_editor):
    ''' Create a few default necessary values for `NotificationInterval` '''
    NotificationInterval = apps.get_model('userprofile',
                                          'NotificationInterval')
    db_alias = schema_editor.connection.alias
    NotificationInterval.objects.using(db_alias).bulk_create([
        NotificationInterval(name='Weekly', days=7),
        NotificationInterval(name='Monthly', days=30),
    ])


def deleteDefaultIntervals(apps, schema_editor):
    ''' Revert the changes by `createDefaultIntervals` '''
    NotificationInterval = apps.get_model('userprofile',
                                          'NotificationInterval')
    db_alias = schema_editor.connection.alias
    NotificationInterval.objects.using(db_alias).filter(
        name='Weekly', days=7).delete()
    NotificationInterval.objects.using(db_alias).filter(
        name='Monthly', days=30).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('groupaccount', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationInterval',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('days', models.IntegerField()),
            ],
        ),
        migrations.RunPython(
            createDefaultIntervals, deleteDefaultIntervals),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('displayname', models.CharField(max_length=15, validators=[django.core.validators.RegexValidator('^\\S.*\\S$|^\\S$|^$', 'This field cannot start or end with spaces.')])),
                ('firstname', models.CharField(max_length=100, blank=True)),
                ('lastname', models.CharField(max_length=100, blank=True)),
                ('showTableView', models.BooleanField(default=False)),
                ('group_accounts', models.ManyToManyField(to='groupaccount.GroupAccount', blank=True)),
                ('historyEmailInterval', models.ForeignKey(to='userprofile.NotificationInterval', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
