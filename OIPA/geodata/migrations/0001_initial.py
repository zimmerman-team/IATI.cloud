# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('iati_vocabulary', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Adm1Region',
            fields=[
                ('adm1_code', models.CharField(max_length=10, serialize=False, primary_key=True)),
                ('OBJECTID_1', models.IntegerField(null=True, blank=True)),
                ('diss_me', models.IntegerField(null=True, blank=True)),
                ('adm1_cod_1', models.CharField(max_length=20, null=True, blank=True)),
                ('iso_3166_2', models.CharField(max_length=2, null=True, blank=True)),
                ('wikipedia', models.CharField(max_length=150, null=True, blank=True)),
                ('adm0_sr', models.IntegerField(null=True, blank=True)),
                ('name', models.CharField(max_length=100, null=True, blank=True)),
                ('name_alt', models.CharField(max_length=200, null=True, blank=True)),
                ('name_local', models.CharField(max_length=100, null=True, blank=True)),
                ('type', models.CharField(max_length=100, null=True, blank=True)),
                ('type_en', models.CharField(max_length=100, null=True, blank=True)),
                ('code_local', models.CharField(max_length=100, null=True, blank=True)),
                ('code_hasc', models.CharField(max_length=100, null=True, blank=True)),
                ('note', models.TextField(null=True, blank=True)),
                ('hasc_maybe', models.CharField(max_length=100, null=True, blank=True)),
                ('region', models.CharField(max_length=100, null=True, blank=True)),
                ('region_cod', models.CharField(max_length=100, null=True, blank=True)),
                ('provnum_ne', models.IntegerField(null=True, blank=True)),
                ('gadm_level', models.IntegerField(null=True, blank=True)),
                ('check_me', models.IntegerField(null=True, blank=True)),
                ('scalerank', models.IntegerField(null=True, blank=True)),
                ('datarank', models.IntegerField(null=True, blank=True)),
                ('abbrev', models.CharField(max_length=100, null=True, blank=True)),
                ('postal', models.CharField(max_length=100, null=True, blank=True)),
                ('area_sqkm', models.CharField(max_length=100, null=True, blank=True)),
                ('sameascity', models.IntegerField(null=True, blank=True)),
                ('labelrank', models.IntegerField(null=True, blank=True)),
                ('featurecla', models.CharField(max_length=100, null=True, blank=True)),
                ('name_len', models.IntegerField(null=True, blank=True)),
                ('mapcolor9', models.IntegerField(null=True, blank=True)),
                ('mapcolor13', models.IntegerField(null=True, blank=True)),
                ('fips', models.CharField(max_length=100, null=True, blank=True)),
                ('fips_alt', models.CharField(max_length=100, null=True, blank=True)),
                ('woe_id', models.IntegerField(null=True, blank=True)),
                ('woe_label', models.CharField(max_length=100, null=True, blank=True)),
                ('woe_name', models.CharField(max_length=100, null=True, blank=True)),
                ('center_location', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, blank=True)),
                ('sov_a3', models.CharField(max_length=3, null=True, blank=True)),
                ('adm0_a3', models.CharField(max_length=3, null=True, blank=True)),
                ('adm0_label', models.IntegerField(null=True, blank=True)),
                ('admin', models.CharField(max_length=100, null=True, blank=True)),
                ('geonunit', models.CharField(max_length=100, null=True, blank=True)),
                ('gu_a3', models.CharField(max_length=3, null=True, blank=True)),
                ('gn_id', models.IntegerField(null=True, blank=True)),
                ('gn_name', models.CharField(max_length=100, null=True, blank=True)),
                ('gns_id', models.IntegerField(null=True, blank=True)),
                ('gns_name', models.CharField(max_length=100, null=True, blank=True)),
                ('gn_level', models.IntegerField(null=True, blank=True)),
                ('gn_region', models.CharField(max_length=100, null=True, blank=True)),
                ('gn_a1_code', models.CharField(max_length=100, null=True, blank=True)),
                ('region_sub', models.CharField(max_length=100, null=True, blank=True)),
                ('sub_code', models.CharField(max_length=100, null=True, blank=True)),
                ('gns_level', models.IntegerField(null=True, blank=True)),
                ('gns_lang', models.CharField(max_length=100, null=True, blank=True)),
                ('gns_adm1', models.CharField(max_length=100, null=True, blank=True)),
                ('gns_region', models.CharField(max_length=100, null=True, blank=True)),
                ('polygon', models.TextField(null=True, blank=True)),
                ('geometry_type', models.CharField(max_length=50, null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'admin1 regions',
            },
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('geoname_id', models.IntegerField(null=True, blank=True)),
                ('name', models.CharField(max_length=200)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, blank=True)),
                ('ascii_name', models.CharField(max_length=200, null=True, blank=True)),
                ('alt_name', models.CharField(max_length=200, null=True, blank=True)),
                ('namepar', models.CharField(max_length=200, null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'cities',
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('code', models.CharField(max_length=2, serialize=False, primary_key=True)),
                ('numerical_code_un', models.IntegerField(null=True, blank=True)),
                ('name', models.CharField(max_length=100, db_index=True)),
                ('alt_name', models.CharField(max_length=100, null=True, blank=True)),
                ('language', models.CharField(max_length=2, null=True)),
                ('dac_country_code', models.IntegerField(null=True, blank=True)),
                ('iso3', models.CharField(max_length=3, null=True, blank=True)),
                ('alpha3', models.CharField(max_length=3, null=True, blank=True)),
                ('fips10', models.CharField(max_length=2, null=True, blank=True)),
                ('center_longlat', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, blank=True)),
                ('polygon', models.TextField(null=True, blank=True)),
                ('data_source', models.CharField(max_length=20, null=True, blank=True)),
                ('capital_city', models.OneToOneField(related_name='capital_of', null=True, blank=True, to='geodata.City')),
            ],
            options={
                'verbose_name_plural': 'countries',
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('code', models.CharField(max_length=100, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=80)),
                ('center_longlat', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, blank=True)),
                ('parental_region', models.ForeignKey(blank=True, to='geodata.Region', null=True)),
                ('region_vocabulary', models.ForeignKey(default=1, to='iati_vocabulary.RegionVocabulary')),
            ],
        ),
        migrations.AddField(
            model_name='country',
            name='region',
            field=models.ForeignKey(blank=True, to='geodata.Region', null=True),
        ),
        migrations.AddField(
            model_name='country',
            name='un_region',
            field=models.ForeignKey(related_name='un_countries', blank=True, to='geodata.Region', null=True),
        ),
        migrations.AddField(
            model_name='country',
            name='unesco_region',
            field=models.ForeignKey(related_name='unesco_countries', blank=True, to='geodata.Region', null=True),
        ),
        migrations.AddField(
            model_name='city',
            name='country',
            field=models.ForeignKey(blank=True, to='geodata.Country', null=True),
        ),
        migrations.AddField(
            model_name='adm1region',
            name='country',
            field=models.ForeignKey(blank=True, to='geodata.Country', null=True),
        ),
    ]
