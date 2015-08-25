# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0001_initial'),
        ('geodata', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='region',
            name='region_vocabulary',
            field=models.ForeignKey(default=1, to='iati.RegionVocabulary'),
        ),
    ]
