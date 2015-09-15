# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0011_auto_20150908_0643'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='description',
            name='description',
        ),
        migrations.RemoveField(
            model_name='result',
            name='description',
        ),
        migrations.RemoveField(
            model_name='result',
            name='title',
        ),
        migrations.RemoveField(
            model_name='title',
            name='language',
        ),
        migrations.RemoveField(
            model_name='title',
            name='title',
        ),
        migrations.AlterField(
            model_name='result',
            name='activity',
            field=models.ForeignKey(to='iati.Activity'),
        ),
    ]
