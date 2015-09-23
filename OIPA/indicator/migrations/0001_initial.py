# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import indicator.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('geodata', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CsvUploadLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('upload_date', models.DateTimeField(auto_now_add=True, verbose_name='Upload date')),
                ('upload', models.FileField(max_length=255, upload_to=indicator.models.file_upload_to, null=True, verbose_name='File', blank=True)),
                ('title', models.CharField(max_length=100, null=True, verbose_name='title', blank=True)),
                ('slug', models.SlugField(unique=True, max_length=100, verbose_name='slug')),
                ('link', models.URLField(max_length=500, null=True, verbose_name='link', blank=True)),
                ('description', models.CharField(max_length=200, verbose_name='description', blank=True)),
                ('cities_not_found', models.TextField(null=True, blank=True)),
                ('countries_not_found', models.TextField(null=True, blank=True)),
                ('total_countries_found', models.IntegerField(null=True, blank=True)),
                ('total_countries_not_found', models.IntegerField(null=True, blank=True)),
                ('total_cities_not_found', models.IntegerField(null=True, blank=True)),
                ('total_cities_found', models.IntegerField(null=True, blank=True)),
                ('total_items_saved', models.IntegerField(null=True, blank=True)),
                ('uploaded_by', models.ForeignKey(related_name='uploaded_files', verbose_name='uploaded by', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='IncomeLevel',
            fields=[
                ('id', models.CharField(max_length=10, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Indicator',
            fields=[
                ('id', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('friendly_label', models.CharField(max_length=255, null=True, blank=True)),
                ('type_data', models.CharField(max_length=255, null=True, blank=True)),
                ('deprivation_type', models.CharField(max_length=255, null=True, blank=True)),
                ('category', models.CharField(max_length=50, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='IndicatorData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('selection_type', models.CharField(max_length=255, null=True, blank=True)),
                ('city', models.ForeignKey(to='geodata.City', null=True)),
                ('country', models.ForeignKey(to='geodata.Country', null=True)),
                ('indicator', models.ForeignKey(to='indicator.Indicator')),
                ('region', models.ForeignKey(to='geodata.Region', null=True)),
            ],
            options={
                'verbose_name_plural': 'indicator data',
            },
        ),
        migrations.CreateModel(
            name='IndicatorDataValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField(db_index=True)),
                ('value', models.DecimalField(db_index=True, null=True, max_digits=17, decimal_places=4, blank=True)),
                ('indicator_data', models.ForeignKey(related_name='values', to='indicator.IndicatorData')),
            ],
        ),
        migrations.CreateModel(
            name='IndicatorSource',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='IndicatorTopic',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('source_note', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LendingType',
            fields=[
                ('id', models.CharField(max_length=10, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='indicator',
            name='source',
            field=models.ForeignKey(blank=True, to='indicator.IndicatorSource', null=True),
        ),
        migrations.AddField(
            model_name='indicator',
            name='topic',
            field=models.ForeignKey(blank=True, to='indicator.IndicatorTopic', null=True),
        ),
    ]
