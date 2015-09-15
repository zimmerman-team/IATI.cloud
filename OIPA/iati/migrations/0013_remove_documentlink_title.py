# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0012_auto_20150914_0719'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='documentlink',
            name='title',
        ),
    ]
