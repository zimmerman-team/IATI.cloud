# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iati_synchroniser', '0002_auto_20150210_1739'),
    ]

    operations = [
        migrations.AlterField(
            model_name='iatixmlsource',
            name='ref',
            field=models.CharField(max_length=70),
        ),
        migrations.AlterField(
            model_name='publisher',
            name='default_interval',
            field=models.CharField(default=b'MONTHLY', max_length=55, choices=[(b'YEARLY', b'Parse yearly'), (b'MONTHLY', b'Parse monthly'), (b'WEEKLY', b'Parse weekly'), (b'DAILY', b'Parse daily')]),
        ),
    ]
