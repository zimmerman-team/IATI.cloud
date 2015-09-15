# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0013_remove_documentlink_title'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activitypolicymarker',
            name='alt_policy_marker',
        ),
        migrations.RemoveField(
            model_name='activitysector',
            name='alt_sector_name',
        ),
    ]
