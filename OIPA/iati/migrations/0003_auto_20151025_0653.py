# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0002_auto_20151023_0938'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activityparticipatingorganisation',
            name='ref',
            field=models.CharField(default=b'', max_length=250, null=True),
        ),
    ]
