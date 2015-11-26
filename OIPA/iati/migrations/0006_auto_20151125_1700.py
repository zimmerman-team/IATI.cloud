# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0005_auto_20151118_1625'),
        ('iati_organisation', '0001_initial')
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityAggregation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('budget_value', models.DecimalField(null=True, max_digits=15, decimal_places=2)),
                ('budget_currency', models.CharField(default=None, max_length=3, null=True)),
                ('disbursement_value', models.DecimalField(null=True, max_digits=15, decimal_places=2)),
                ('disbursement_currency', models.CharField(default=None, max_length=3, null=True)),
                ('incoming_funds_value', models.DecimalField(null=True, max_digits=15, decimal_places=2)),
                ('incoming_funds_currency', models.CharField(default=None, max_length=3, null=True)),
                ('commitment_value', models.DecimalField(null=True, max_digits=15, decimal_places=2)),
                ('commitment_currency', models.CharField(default=None, max_length=3, null=True)),
                ('expenditure_value', models.DecimalField(null=True, max_digits=15, decimal_places=2)),
                ('expenditure_currency', models.CharField(default=None, max_length=3, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ActivityPlusChildAggregation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('budget_value', models.DecimalField(null=True, max_digits=15, decimal_places=2)),
                ('budget_currency', models.CharField(default=None, max_length=3, null=True)),
                ('disbursement_value', models.DecimalField(null=True, max_digits=15, decimal_places=2)),
                ('disbursement_currency', models.CharField(default=None, max_length=3, null=True)),
                ('incoming_funds_value', models.DecimalField(null=True, max_digits=15, decimal_places=2)),
                ('incoming_funds_currency', models.CharField(default=None, max_length=3, null=True)),
                ('commitment_value', models.DecimalField(null=True, max_digits=15, decimal_places=2)),
                ('commitment_currency', models.CharField(default=None, max_length=3, null=True)),
                ('expenditure_value', models.DecimalField(null=True, max_digits=15, decimal_places=2)),
                ('expenditure_currency', models.CharField(default=None, max_length=3, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ChildAggregation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('budget_value', models.DecimalField(null=True, max_digits=15, decimal_places=2)),
                ('budget_currency', models.CharField(default=None, max_length=3, null=True)),
                ('disbursement_value', models.DecimalField(null=True, max_digits=15, decimal_places=2)),
                ('disbursement_currency', models.CharField(default=None, max_length=3, null=True)),
                ('incoming_funds_value', models.DecimalField(null=True, max_digits=15, decimal_places=2)),
                ('incoming_funds_currency', models.CharField(default=None, max_length=3, null=True)),
                ('commitment_value', models.DecimalField(null=True, max_digits=15, decimal_places=2)),
                ('commitment_currency', models.CharField(default=None, max_length=3, null=True)),
                ('expenditure_value', models.DecimalField(null=True, max_digits=15, decimal_places=2)),
                ('expenditure_currency', models.CharField(default=None, max_length=3, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='organisation',
            name='type',
        ),
        migrations.RemoveField(
            model_name='activity',
            name='activity_aggregations',
        ),
        migrations.AlterField(
            model_name='activityparticipatingorganisation',
            name='organisation',
            field=models.ForeignKey(default=None, to='iati_organisation.Organisation', null=True),
        ),
        migrations.AlterField(
            model_name='activityreportingorganisation',
            name='organisation',
            field=models.ForeignKey(default=None, to='iati_organisation.Organisation', null=True),
        ),
        migrations.AlterField(
            model_name='transactionprovider',
            name='organisation',
            field=models.ForeignKey(related_name='transaction_providing_organisation', on_delete=django.db.models.deletion.SET_NULL, default=None, to='iati_organisation.Organisation', null=True),
        ),
        migrations.AlterField(
            model_name='transactionprovider',
            name='provider_activity',
            field=models.ForeignKey(related_name='transaction_provider_activity', on_delete=django.db.models.deletion.SET_NULL, default=None, to='iati.Activity', null=True),
        ),
        migrations.AlterField(
            model_name='transactionreceiver',
            name='organisation',
            field=models.ForeignKey(related_name='transaction_receiving_organisation', on_delete=django.db.models.deletion.SET_NULL, default=None, to='iati_organisation.Organisation', null=True),
        ),
        migrations.AlterField(
            model_name='transactionreceiver',
            name='receiver_activity',
            field=models.ForeignKey(related_name='transaction_receiver_activity', on_delete=django.db.models.deletion.SET_NULL, default=None, to='iati.Activity', null=True),
        ),
        migrations.DeleteModel(
            name='ActivityAggregationData',
        ),
        migrations.DeleteModel(
            name='Organisation',
        ),
        migrations.AddField(
            model_name='childaggregation',
            name='activity',
            field=models.OneToOneField(related_name='child_aggregation', default=None, to='iati.Activity'),
        ),
        migrations.AddField(
            model_name='activitypluschildaggregation',
            name='activity',
            field=models.OneToOneField(related_name='activity_plus_child_aggregation', default=None, to='iati.Activity'),
        ),
        migrations.AddField(
            model_name='activityaggregation',
            name='activity',
            field=models.OneToOneField(related_name='activity_aggregation', default=None, to='iati.Activity'),
        ),
    ]
