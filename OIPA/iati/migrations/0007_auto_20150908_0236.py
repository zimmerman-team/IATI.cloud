# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0006_auto_20150905_0454'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fss',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('extraction_date', models.DateField(default=None, null=True)),
                ('priority', models.BooleanField(default=False)),
                ('phaseout_year', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='FssForecast',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField(null=True)),
                ('value_date', models.DateField(default=None, null=True)),
                ('value', models.DecimalField(max_digits=15, decimal_places=2)),
                ('currency', models.ForeignKey(to='iati.Currency')),
                ('fss', models.ForeignKey(to='iati.Fss')),
            ],
        ),
        migrations.CreateModel(
            name='TransactionReceiver',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=255)),
            ],
        ),
        migrations.RemoveField(
            model_name='ffs',
            name='activity',
        ),
        migrations.RemoveField(
            model_name='ffsforecast',
            name='currency',
        ),
        migrations.RemoveField(
            model_name='ffsforecast',
            name='ffs',
        ),
        migrations.RemoveField(
            model_name='transactionreciever',
            name='organisation',
        ),
        migrations.RemoveField(
            model_name='transactionreciever',
            name='transaction',
        ),
        migrations.RemoveField(
            model_name='activity',
            name='end_actual',
        ),
        migrations.RemoveField(
            model_name='activity',
            name='end_planned',
        ),
        migrations.RemoveField(
            model_name='activity',
            name='start_actual',
        ),
        migrations.RemoveField(
            model_name='activity',
            name='start_planned',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='provider_organisation',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='provider_organisation_name',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='receiver_organisation',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='receiver_organisation_name',
        ),
        migrations.AddField(
            model_name='transaction',
            name='receiver_activity',
            field=models.ForeignKey(related_name='transaction_receiver_activity', db_constraint=False, to='iati.Activity', null=True),
        ),
        migrations.AlterField(
            model_name='activitydate',
            name='iso_date',
            field=models.DateField(default=b'1970-01-01'),
        ),
        migrations.AlterField(
            model_name='legacydata',
            name='iati_equivalent',
            field=models.CharField(max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='narrative',
            name='iati_identifier',
            field=models.CharField(max_length=250, null=True, verbose_name=b'iati_identifier'),
        ),
        migrations.AlterField(
            model_name='narrative',
            name='object_id',
            field=models.CharField(max_length=250, null=True, verbose_name=b'related object'),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='code',
            field=models.CharField(max_length=250, serialize=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='reported_by_organisation',
            field=models.CharField(default=b'', max_length=150),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='provider_activity',
            field=models.ForeignKey(related_name='transaction_provider_activity', db_constraint=False, to='iati.Activity', null=True),
        ),
        migrations.DeleteModel(
            name='Ffs',
        ),
        migrations.DeleteModel(
            name='FfsForecast',
        ),
        migrations.DeleteModel(
            name='TransactionReciever',
        ),
        migrations.AddField(
            model_name='transactionreceiver',
            name='organisation',
            field=models.ForeignKey(related_name='transaction_receiving_organisation', default=None, to='iati.Organisation', null=True),
        ),
        migrations.AddField(
            model_name='transactionreceiver',
            name='transaction',
            field=models.ForeignKey(to='iati.Transaction'),
        ),
        migrations.AddField(
            model_name='fss',
            name='activity',
            field=models.ForeignKey(to='iati.Activity'),
        ),
    ]
