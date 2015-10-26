# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0005_auto_20151026_0710'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='description',
            field=models.OneToOneField(related_name='transaction_description', null=True, to='iati.TransactionDescription'),
        ),
    ]
