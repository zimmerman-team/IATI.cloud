# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0004_auto_20151117_1023'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='narrative',
            name='parent_content_type',
        ),
        migrations.AddField(
            model_name='narrative',
            name='activity',
            field=models.ForeignKey(default=None, to='iati.Activity', null=True),
        ),
        migrations.RunSQL("UPDATE iati_narrative SET activity_id = parent_object_id"),
        migrations.RemoveField(
            model_name='narrative',
            name='parent_object_id',
        ),
        migrations.AlterField(
            model_name='narrative',
            name='activity',
            field=models.ForeignKey(to='iati.Activity'),
        ),
        migrations.AlterIndexTogether(
            name='narrative',
            index_together=set([('related_content_type', 'related_object_id')]),
        ),
    ]
