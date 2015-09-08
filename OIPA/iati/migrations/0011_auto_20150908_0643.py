# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0010_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='narrative',
            name='iati_identifier',
            field=models.CharField(max_length=150, null=True, verbose_name=b'iati_identifier'),
        ),
    ]
