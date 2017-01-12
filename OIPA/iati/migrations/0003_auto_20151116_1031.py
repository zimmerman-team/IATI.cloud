# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0002_auto_20151104_1515'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='end_date',
            field=models.DateField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='start_date',
            field=models.DateField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='activityaggregationdata',
            name='total_plus_child_budget_currency',
            field=models.CharField(default=None, max_length=3, null=True),
        ),
        migrations.AddField(
            model_name='activityaggregationdata',
            name='total_plus_child_budget_value',
            field=models.DecimalField(null=True, max_digits=15, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='activityparticipatingorganisation',
            name='normalized_ref',
            field=models.CharField(default=b'', max_length=120, db_index=True),
        ),
    ]
