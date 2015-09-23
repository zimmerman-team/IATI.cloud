# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BudgetIdentifierVocabulary',
            fields=[
                ('code', models.SmallIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='GeographicVocabulary',
            fields=[
                ('code', models.CharField(max_length=20, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(default=b'')),
                ('url', models.URLField()),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PolicyMarkerVocabulary',
            fields=[
                ('code', models.CharField(max_length=10, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RegionVocabulary',
            fields=[
                ('code', models.SmallIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SectorVocabulary',
            fields=[
                ('code', models.CharField(max_length=10, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(default=b'')),
                ('url', models.URLField()),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Vocabulary',
            fields=[
                ('code', models.CharField(max_length=10, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=140)),
                ('description', models.TextField(default=b'')),
                ('codelist_iati_version', models.CharField(max_length=4)),
                ('codelist_successor', models.CharField(max_length=100, null=True)),
            ],
        ),
    ]
