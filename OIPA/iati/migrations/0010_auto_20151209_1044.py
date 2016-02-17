# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0009_auto_20151208_1423'),
    ]

    operations = [
        # migrations.AlterField(
        #     model_name='resultindicatorperiod',
        #     name='period_end',
        #     field=models.DateField(null=True, blank=True),
        # ),
        # migrations.AlterField(
        #     model_name='resultindicatorperiod',
        #     name='period_start',
        #     field=models.DateField(null=True, blank=True),
        # ),
        migrations.RunSQL(
            'ALTER TABLE "iati_resultindicatorperiod" ALTER COLUMN "period_start" type date USING ("period_start"::date);',
            'ALTER TABLE "iati_resultindicatorperiod" ALTER COLUMN "period_start" type varchar(50)'
        ),
        migrations.RunSQL(
            'ALTER TABLE "iati_resultindicatorperiod" ALTER COLUMN "period_end" type date USING ("period_end"::date);',
            'ALTER TABLE "iati_resultindicatorperiod" ALTER COLUMN "period_end" type varchar(50)'
        ),
        migrations.RemoveField(
            model_name='resultindicatormeasure',
            name='result_indicator',
        ),
        migrations.RemoveField(
            model_name='resultindicator',
            name='description',
        ),
        migrations.RemoveField(
            model_name='resultindicator',
            name='title',
        ),
        migrations.RemoveField(
            model_name='resultindicatorperiod',
            name='planned_disbursement_period_end',
        ),
        migrations.RemoveField(
            model_name='resultindicatorperiod',
            name='planned_disbursement_period_start',
        ),
        migrations.AddField(
            model_name='resultindicator',
            name='ascending',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='resultdescription',
            name='result',
            field=models.OneToOneField(to='iati.Result'),
        ),
        migrations.AlterField(
            model_name='resultindicatorbaselinecomment',
            name='result_indicator',
            field=models.OneToOneField(to='iati.ResultIndicator'),
        ),
        migrations.AlterField(
            model_name='resultindicatordescription',
            name='result_indicator',
            field=models.OneToOneField(to='iati.ResultIndicator'),
        ),
        migrations.AlterField(
            model_name='resultindicatorperiodactualcomment',
            name='result_indicator_period',
            field=models.OneToOneField(to='iati.ResultIndicatorPeriod'),
        ),
        migrations.AlterField(
            model_name='resultindicatorperiodtargetcomment',
            name='result_indicator_period',
            field=models.OneToOneField(to='iati.ResultIndicatorPeriod'),
        ),
        migrations.AlterField(
            model_name='resultindicatortitle',
            name='result_indicator',
            field=models.OneToOneField(to='iati.ResultIndicator'),
        ),
        migrations.AlterField(
            model_name='resulttitle',
            name='result',
            field=models.OneToOneField(to='iati.Result'),
        ),
        migrations.DeleteModel(
            name='ResultIndicatorMeasure',
        ),
    ]
