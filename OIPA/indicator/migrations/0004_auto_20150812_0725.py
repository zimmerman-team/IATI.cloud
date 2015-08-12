# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('indicator', '0003_auto_20150812_0622'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indicatordatavalue',
            name='year',
            field=models.IntegerField(db_index=True),
        ),
    ]
