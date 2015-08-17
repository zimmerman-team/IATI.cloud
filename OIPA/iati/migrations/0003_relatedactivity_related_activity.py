# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0002_activityrecipientregion_region_vocabulary'),
    ]

    operations = [
        migrations.AddField(
            model_name='relatedactivity',
            name='related_activity',
            field=models.ForeignKey(related_name='related_activity', on_delete=django.db.models.deletion.SET_NULL, to='iati.Activity', null=True),
        ),
    ]
