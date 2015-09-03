# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0003_auto_20150903_0333'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activity',
            name='total_budget',
        ),
        migrations.RemoveField(
            model_name='activity',
            name='total_budget_currency',
        ),
    ]
