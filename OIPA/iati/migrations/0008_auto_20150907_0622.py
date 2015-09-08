# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0007_auto_20150907_0550'),
    ]

    operations = [
        migrations.AlterField(
            model_name='narrative',
            name='object_id',
            field=models.CharField(max_length=250, null=True, verbose_name=b'related object'),
        ),
    ]
