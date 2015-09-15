# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0014_auto_20150914_0857'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='activity_description',
        ),
        migrations.RemoveField(
            model_name='location',
            name='description',
        ),
        migrations.RemoveField(
            model_name='location',
            name='name',
        ),
    ]
