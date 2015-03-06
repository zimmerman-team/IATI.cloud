# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('indicator', '0002_auto_20150123_0840'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indicatordatavalue',
            name='indicator_data',
            field=models.ForeignKey(related_name='values', to='indicator.IndicatorData'),
            preserve_default=True,
        ),
    ]
