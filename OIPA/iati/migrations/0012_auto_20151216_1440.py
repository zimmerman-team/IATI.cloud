# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0011_auto_20151210_1254'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='activity',
            options={'ordering': ['id'], 'verbose_name_plural': 'activities'},
        ),
        migrations.AlterField(
            model_name='activity',
            name='actual_end',
            field=models.DateField(default=None, null=True, db_index=True, blank=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='actual_start',
            field=models.DateField(default=None, null=True, db_index=True, blank=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='end_date',
            field=models.DateField(default=None, null=True, db_index=True, blank=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='planned_end',
            field=models.DateField(default=None, null=True, db_index=True, blank=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='planned_start',
            field=models.DateField(default=None, null=True, db_index=True, blank=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='start_date',
            field=models.DateField(default=None, null=True, db_index=True, blank=True),
        ),
        migrations.AlterField(
            model_name='activityaggregation',
            name='budget_value',
            field=models.DecimalField(db_index=True, null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='activityaggregation',
            name='commitment_value',
            field=models.DecimalField(db_index=True, null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='activityaggregation',
            name='disbursement_value',
            field=models.DecimalField(db_index=True, null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='activityaggregation',
            name='expenditure_value',
            field=models.DecimalField(db_index=True, null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='activityaggregation',
            name='incoming_funds_value',
            field=models.DecimalField(db_index=True, null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='activitypluschildaggregation',
            name='budget_value',
            field=models.DecimalField(db_index=True, null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='activitypluschildaggregation',
            name='commitment_value',
            field=models.DecimalField(db_index=True, null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='activitypluschildaggregation',
            name='disbursement_value',
            field=models.DecimalField(db_index=True, null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='activitypluschildaggregation',
            name='expenditure_value',
            field=models.DecimalField(db_index=True, null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='activitypluschildaggregation',
            name='incoming_funds_value',
            field=models.DecimalField(db_index=True, null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='childaggregation',
            name='budget_value',
            field=models.DecimalField(db_index=True, null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='childaggregation',
            name='commitment_value',
            field=models.DecimalField(db_index=True, null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='childaggregation',
            name='disbursement_value',
            field=models.DecimalField(db_index=True, null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='childaggregation',
            name='expenditure_value',
            field=models.DecimalField(db_index=True, null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='childaggregation',
            name='incoming_funds_value',
            field=models.DecimalField(db_index=True, null=True, max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AlterIndexTogether(
            name='activity',
            index_together=set([('actual_end', 'id'), ('actual_start', 'id'), ('start_date', 'id'), ('end_date', 'id'), ('planned_end', 'id'), ('planned_start', 'id')]),
        ),
        migrations.AlterIndexTogether(
            name='activityaggregation',
            index_together=set([('incoming_funds_value', 'activity'), ('expenditure_value', 'activity'), ('budget_value', 'activity'), ('commitment_value', 'activity'), ('disbursement_value', 'activity')]),
        ),
        migrations.AlterIndexTogether(
            name='activitypluschildaggregation',
            index_together=set([('incoming_funds_value', 'activity'), ('expenditure_value', 'activity'), ('budget_value', 'activity'), ('commitment_value', 'activity'), ('disbursement_value', 'activity')]),
        ),
        migrations.AlterIndexTogether(
            name='childaggregation',
            index_together=set([('incoming_funds_value', 'activity'), ('expenditure_value', 'activity'), ('budget_value', 'activity'), ('commitment_value', 'activity'), ('disbursement_value', 'activity')]),
        ),
    ]
