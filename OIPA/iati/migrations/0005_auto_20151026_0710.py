# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0004_auto_20151026_0443'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='description',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='description_type',
        ),
        migrations.RemoveField(
            model_name='transactiondescription',
            name='transaction',
        ),
    ]
