# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0003_auto_20151025_0653'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='is_searchable',
            field=models.BooleanField(default=True, db_index=True),
        ),
    ]
