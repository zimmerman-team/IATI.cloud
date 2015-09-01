# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parse_logger', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='parselog',
            name='error_msg',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
