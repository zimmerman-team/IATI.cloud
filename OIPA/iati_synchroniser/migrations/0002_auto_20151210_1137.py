# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iati_synchroniser', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='iatixmlsource',
            name='source_url',
            field=models.URLField(unique=True, max_length=255),
        ),
    ]
