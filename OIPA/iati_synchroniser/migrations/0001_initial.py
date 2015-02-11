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
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IatiXmlSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ref', models.CharField(help_text='Reference for the XML file. Preferred usage: Name on IATI registry', max_length=70, verbose_name='Reference')),
                ('title', models.CharField(max_length=255)),
                ('type', models.IntegerField(default=1, choices=[(1, 'Activity Files'), (2, 'Organisation Files')])),
                ('source_url', models.CharField(help_text='Hyperlink to an iati activity or organisation XML file.', unique=True, max_length=255)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now_add=True)),
                ('update_interval', models.CharField(default=b'month', max_length=20, choices=[(b'day', 'Day'), (b'week', 'Week'), (b'month', 'Month'), (b'year', 'Year')])),
                ('last_found_in_registry', models.DateTimeField(default=None, null=True)),
                ('xml_activity_count', models.IntegerField(default=None, null=True)),
                ('oipa_activity_count', models.IntegerField(default=None, null=True)),
                ('iati_standard_version', models.CharField(default=b'', max_length=10)),
                ('is_parsed', models.BooleanField(default=False)),
                ('added_manually', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['ref'],
                'verbose_name_plural': 'IATI XML sources',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Publisher',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('org_id', models.CharField(max_length=100)),
                ('org_abbreviate', models.CharField(max_length=55)),
                ('org_name', models.CharField(max_length=255)),
                ('default_interval', models.CharField(default='MONTHLY', max_length=55, verbose_name='Interval', choices=[('YEARLY', 'Parse yearly'), ('MONTHLY', 'Parse monthly'), ('WEEKLY', 'Parse weekly'), ('DAILY', 'Parse daily')])),
                ('XML_total_activity_count', models.IntegerField(default=None, null=True)),
                ('OIPA_total_activity_count', models.IntegerField(default=None, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='iatixmlsource',
            name='publisher',
            field=models.ForeignKey(to='iati_synchroniser.Publisher'),
            preserve_default=True,
        ),
    ]
