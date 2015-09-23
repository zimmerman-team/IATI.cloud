# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('geodata', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnescoIndicator',
            fields=[
                ('id', models.CharField(max_length=50, serialize=False, primary_key=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('friendly_label', models.CharField(max_length=255, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='UnescoIndicatorData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.FloatField(null=True, blank=True)),
                ('type_value', models.IntegerField(null=True, blank=True)),
                ('website', models.CharField(max_length=255, null=True, blank=True)),
                ('created', models.DateTimeField(auto_now=True)),
                ('updated', models.DateTimeField(auto_now_add=True)),
                ('country', models.ForeignKey(to='geodata.Country', null=True)),
                ('unesco_indicator', models.ForeignKey(to='indicator_unesco.UnescoIndicator')),
            ],
            options={
                'verbose_name_plural': 'Unesco indicator data',
            },
        ),
    ]
