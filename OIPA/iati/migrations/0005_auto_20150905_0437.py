# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0004_auto_20150903_0408'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='documentlink',
            name='document_category',
        ),
        migrations.AddField(
            model_name='documentlink',
            name='categories',
            field=models.ManyToManyField(to='iati.DocumentCategory'),
        ),
    ]
