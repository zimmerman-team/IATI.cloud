# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.contrib.contenttypes.management import update_contenttypes
import django.db.models.deletion


def remove_planned_disbursements(apps, schema_editor):
    """
    add budget status 1 as its used as default in iati migration 0036
    """
    update_contenttypes(apps.get_app_config('iati'), interactive=False) # make sure all content types exist

    try: # don't run on first migration
        PlannedDisbursement = apps.get_model('iati', 'PlannedDisbursement')
    except:
        return

    PlannedDisbursement.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0034_auto_20160524_1548'),
    ]

    operations = [
        migrations.RunPython(remove_planned_disbursements),
        migrations.AddField(
            model_name='resultindicatortitle',
            name='primary_name',
            field=models.CharField(blank=True, db_index=True, default=b'', max_length=255),
        ),
        migrations.AlterField(
            model_name='resultindicatorperiod',
            name='actual',
            field=models.CharField(blank=True, default=None, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='resultindicatorperiod',
            name='target',
            field=models.CharField(blank=True, default=None, max_length=50, null=True),
        ),
    ]
