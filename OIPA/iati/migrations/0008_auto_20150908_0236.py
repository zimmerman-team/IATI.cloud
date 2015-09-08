# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0007_auto_20150908_0236'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='provider_organisation',
            field=models.ForeignKey(related_name='transaction_receiver_activity', to='iati.TransactionProvider', null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='receiver_organisation',
            field=models.ForeignKey(related_name='transaction_receiver_activity', to='iati.TransactionReceiver', null=True),
        ),
    ]
