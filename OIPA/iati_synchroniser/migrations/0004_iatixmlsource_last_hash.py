# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iati_synchroniser', '0003_auto_20150211_0707'),
    ]

    operations = [
        migrations.AddField(
            model_name='iatixmlsource',
            name='last_hash',
            field=models.CharField(default=b'', max_length=32),
            preserve_default=True,
        ),
    ]
