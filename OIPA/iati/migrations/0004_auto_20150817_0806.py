# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0003_relatedactivity_related_activity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='budget',
            name='period_end',
            field=models.DateField(default=None, blank=True),
        ),
        migrations.AlterField(
            model_name='budget',
            name='period_start',
            field=models.DateField(default=None, blank=True),
        ),
    ]
