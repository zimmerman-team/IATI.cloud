# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0008_auto_20151203_1403'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activityreportingorganisation',
            name='normalized_ref',
            field=models.CharField(default=b'', max_length=120, db_index=True),
        ),
        migrations.AlterField(
            model_name='activityreportingorganisation',
            name='ref',
            field=models.CharField(max_length=250, db_index=True),
        ),
    ]
