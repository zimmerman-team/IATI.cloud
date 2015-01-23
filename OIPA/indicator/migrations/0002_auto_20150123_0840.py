# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('indicator', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IndicatorDataValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField(max_length=5, db_index=True)),
                ('value', models.DecimalField(db_index=True, null=True, max_digits=17, decimal_places=4, blank=True)),
                ('indicator_data', models.ForeignKey(to='indicator.IndicatorData')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='indicatordata',
            name='value',
        ),
        migrations.RemoveField(
            model_name='indicatordata',
            name='year',
        ),
    ]
