# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='xdr_value',
            field=models.DecimalField(default=0.123456789, max_digits=15, decimal_places=2),
            preserve_default=False,
        ),
    ]
