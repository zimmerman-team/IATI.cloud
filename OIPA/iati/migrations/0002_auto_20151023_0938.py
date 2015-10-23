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
        migrations.RenameField(
            model_name='narrative',
            old_name='object_id',
            new_name='related_object_id',
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
            model_name='relatedactivity',
            name='related_activity',
        ),
        migrations.AddField(
            model_name='activity',
            name='is_searchable',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='last_updated_model',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='narrative',
            name='parent_content_type',
            field=models.ForeignKey(related_name='parent_agent', default=None, to='contenttypes.ContentType'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='narrative',
            name='parent_object_id',
            field=models.CharField(default=None, max_length=250, verbose_name=b'Parent related object'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='narrative',
            name='related_content_type',
            field=models.ForeignKey(related_name='related_agent', default=None, to='contenttypes.ContentType'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='relatedactivity',
            name='ref_activity',
            field=models.ForeignKey(related_name='ref_activity', on_delete=django.db.models.deletion.SET_NULL, to='iati.Activity', null=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='hierarchy',
            field=models.SmallIntegerField(default=1, choices=[(1, 'Parent'), (2, 'Child')]),
        ),
        migrations.AlterField(
            model_name='activity',
            name='title',
            field=models.OneToOneField(default=None, to='iati.Title'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='narrative',
            name='content',
            field=models.TextField(default=None),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='narrative',
            name='language',
            field=models.ForeignKey(default=None, to='iati_codelists.Language'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='relatedactivity',
            name='current_activity',
            field=models.ForeignKey(to='iati.Activity'),
        ),
        migrations.AddField(
            model_name='activity',
            name='activity_aggregations',
            field=models.OneToOneField(null=True, to='iati.ActivityAggregationData'),
        ),
    ]
