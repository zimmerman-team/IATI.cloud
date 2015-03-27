# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0002_auto_20150325_1531'),
    ]

    operations = [
        migrations.AddField(
            model_name='planneddisbursement',
            name='budget_type',
            field=models.ForeignKey(default=None, to='iati.BudgetType', null=True),
            preserve_default=True,
        ),
    ]
