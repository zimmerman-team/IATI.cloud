# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('geodata', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Adm2Region',
            fields=[
                ('code', models.CharField(max_length=10, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100, null=True, blank=True)),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(default=((((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)),),), srid=4326)),
                ('region', models.ForeignKey(to='geodata.Adm1Region')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='adm1region',
            name='geom',
            field=django.contrib.gis.db.models.fields.MultiPolygonField(default=((((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)),),), srid=4326),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='country',
            name='geom',
            field=django.contrib.gis.db.models.fields.MultiPolygonField(default=((((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)),),), srid=4326),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='adm1region',
            name='center_location',
            field=django.contrib.gis.db.models.fields.PointField(srid=4326, blank=True),
        ),
        migrations.AlterField(
            model_name='city',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(srid=4326, blank=True),
        ),
        migrations.AlterField(
            model_name='country',
            name='center_longlat',
            field=django.contrib.gis.db.models.fields.PointField(srid=4326, blank=True),
        ),
        migrations.AlterField(
            model_name='region',
            name='center_longlat',
            field=django.contrib.gis.db.models.fields.PointField(srid=4326, blank=True),
        ),
    ]
