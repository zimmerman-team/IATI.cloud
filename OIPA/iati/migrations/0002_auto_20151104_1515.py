# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('iati', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityAggregationData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('total_budget_value', models.DecimalField(null=True, max_digits=15, decimal_places=2)),
                ('total_budget_currency', models.CharField(default=None, max_length=3, null=True)),
                ('total_child_budget_value', models.DecimalField(null=True, max_digits=15, decimal_places=2)),
                ('total_child_budget_currency', models.CharField(default=None, max_length=3, null=True)),
                ('total_disbursement_value', models.DecimalField(null=True, max_digits=15, decimal_places=2)),
                ('total_disbursement_currency', models.CharField(default=None, max_length=3, null=True)),
                ('total_incoming_funds_value', models.DecimalField(null=True, max_digits=15, decimal_places=2)),
                ('total_incoming_funds_currency', models.CharField(default=None, max_length=3, null=True)),
                ('total_commitment_value', models.DecimalField(null=True, max_digits=15, decimal_places=2)),
                ('total_commitment_currency', models.CharField(default=None, max_length=3, null=True)),
                ('total_expenditure_value', models.DecimalField(null=True, max_digits=15, decimal_places=2)),
                ('total_expenditure_currency', models.CharField(default=None, max_length=3, null=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name='relatedactivity',
            options={'verbose_name_plural': 'related activities'},
        ),
        migrations.RemoveField(
            model_name='activity',
            name='title',
        ),
        migrations.RemoveField(
            model_name='narrative',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='narrative',
            name='iati_identifier',
        ),
        migrations.RemoveField(
            model_name='narrative',
            name='object_id',
        ),
        migrations.RemoveField(
            model_name='relatedactivity',
            name='related_activity',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='description',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='description_type',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='provider_organisation',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='receiver_organisation',
        ),
        migrations.AddField(
            model_name='activity',
            name='actual_end',
            field=models.DateField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='actual_start',
            field=models.DateField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='is_searchable',
            field=models.BooleanField(default=True, db_index=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='last_updated_model',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='planned_end',
            field=models.DateField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='planned_start',
            field=models.DateField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='narrative',
            name='parent_content_type',
            field=models.ForeignKey(related_name='parent_agent', default=1, to='contenttypes.ContentType'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='narrative',
            name='parent_object_id',
            field=models.CharField(default=1, max_length=250, verbose_name=b'Parent related object'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='narrative',
            name='related_content_type',
            field=models.ForeignKey(related_name='related_agent', default=1, to='contenttypes.ContentType'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='narrative',
            name='related_object_id',
            field=models.IntegerField(null=True, verbose_name=b'related object', db_index=True),
        ),
        migrations.AddField(
            model_name='relatedactivity',
            name='ref_activity',
            field=models.ForeignKey(related_name='ref_activity', on_delete=django.db.models.deletion.SET_NULL, to='iati.Activity', null=True),
        ),
        migrations.AddField(
            model_name='title',
            name='activity',
            field=models.OneToOneField(related_name='title', default=1, to='iati.Activity'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transactionprovider',
            name='transaction',
            field=models.OneToOneField(related_name='provider_organisation', default=1, to='iati.Transaction'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transactionreceiver',
            name='transaction',
            field=models.OneToOneField(related_name='receiver_organisation', default=1, to='iati.Transaction'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='activity',
            name='hierarchy',
            field=models.SmallIntegerField(default=1, choices=[(1, 'Parent'), (2, 'Child')]),
        ),
        migrations.AlterField(
            model_name='activityparticipatingorganisation',
            name='ref',
            field=models.CharField(default=b'', max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='narrative',
            name='content',
            field=models.TextField(default='migration'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='narrative',
            name='language',
            field=models.ForeignKey(default=1, to='iati_codelists.Language'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='relatedactivity',
            name='current_activity',
            field=models.ForeignKey(to='iati.Activity'),
        ),
        migrations.AlterField(
            model_name='transactiondescription',
            name='transaction',
            field=models.OneToOneField(related_name='description', to='iati.Transaction'),
        ),
        migrations.AddField(
            model_name='activity',
            name='activity_aggregations',
            field=models.OneToOneField(null=True, to='iati.ActivityAggregationData'),
        ),
    ]
