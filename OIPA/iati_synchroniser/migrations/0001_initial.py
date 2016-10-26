# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Codelist',
            fields=[
                ('name', models.CharField(max_length=100, serialize=False, primary_key=True)),
                ('description', models.TextField(max_length=1000, null=True, blank=True)),
                ('count', models.CharField(max_length=10, null=True, blank=True)),
                ('fields', models.CharField(max_length=255, null=True, blank=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='IatiXmlSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ref', models.CharField(max_length=70)),
                ('title', models.CharField(default=b'', max_length=255)),
                ('type', models.IntegerField(default=1, choices=[(1, b'Activity Files'), (2, b'Organisation Files')])),
                ('source_url', models.CharField(unique=True, max_length=255)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now_add=True)),
                ('update_interval', models.CharField(default=b'month', max_length=20, choices=[(b'day', b'Day'), (b'week', b'Week'), (b'month', b'Month'), (b'year', b'Year')])),
                ('last_found_in_registry', models.DateTimeField(default=None, null=True)),
                ('xml_activity_count', models.IntegerField(default=None, null=True)),
                ('oipa_activity_count', models.IntegerField(default=None, null=True)),
                ('iati_standard_version', models.CharField(default=b'', max_length=10)),
                ('is_parsed', models.BooleanField(default=False)),
                ('added_manually', models.BooleanField(default=True)),
                ('last_hash', models.CharField(default=b'', max_length=32)),
            ],
            options={
                'ordering': ['ref'],
                'verbose_name_plural': 'IATI XML sources',
            },
        ),
        migrations.CreateModel(
            name='Publisher',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('org_id', models.CharField(max_length=100)),
                ('org_abbreviate', models.CharField(default=b'', max_length=55)),
                ('org_name', models.CharField(max_length=255)),
                ('default_interval', models.CharField(default=b'MONTHLY', max_length=55, choices=[(b'YEARLY', b'Parse yearly'), (b'MONTHLY', b'Parse monthly'), (b'WEEKLY', b'Parse weekly'), (b'DAILY', b'Parse daily')])),
                ('XML_total_activity_count', models.IntegerField(default=None, null=True)),
                ('OIPA_total_activity_count', models.IntegerField(default=None, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='iatixmlsource',
            name='publisher',
            field=models.ForeignKey(to='iati_synchroniser.Publisher'),
        ),
    ]
