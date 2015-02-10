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
            name='ref',
            field=models.CharField(max_length=70, verbose_name='Reference'),
        ),
        migrations.AlterField(
            model_name='iatixmlsource',
            name='source_url',
            field=models.CharField(unique=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='iatixmlsource',
            name='title',
            field=models.CharField(default=b'', max_length=255),
        ),
        migrations.AlterField(
            model_name='publisher',
            name='org_abbreviate',
            field=models.CharField(default=b'', max_length=55),
        ),
    ]
