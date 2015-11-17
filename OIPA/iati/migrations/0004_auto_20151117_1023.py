# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0003_auto_20151116_1031'),
    ]

    operations = [
        migrations.AlterField(
            model_name='relatedactivity',
            name='ref',
            field=models.CharField(default=b'', max_length=200, db_index=True),
        ),
        migrations.AlterField(
            model_name='transactionprovider',
            name='provider_activity_ref',
            field=models.CharField(default=b'', max_length=200, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='transactionreceiver',
            name='receiver_activity_ref',
            field=models.CharField(default=b'', max_length=200, null=True, db_index=True),
        ),
    ]
