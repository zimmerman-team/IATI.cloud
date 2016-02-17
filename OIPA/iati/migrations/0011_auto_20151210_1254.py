# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0010_auto_20151209_1044'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='resultindicator',
            name='comment',
        ),
        migrations.AlterField(
            model_name='resultindicator',
            name='baseline_value',
            field=models.CharField(default=None, max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='resultindicator',
            name='baseline_year',
            field=models.IntegerField(default=None, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='resultindicatorperiod',
            name='period_end',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='resultindicatorperiod',
            name='period_start',
            field=models.DateField(null=True, blank=True),
        ),
    ]
