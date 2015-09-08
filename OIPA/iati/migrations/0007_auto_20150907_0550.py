# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0006_auto_20150905_0454'),
    ]

    operations = [
        migrations.AlterField(
            model_name='legacydata',
            name='iati_equivalent',
            field=models.CharField(max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='code',
            field=models.CharField(max_length=250, serialize=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='reported_by_organisation',
            field=models.CharField(default=b'', max_length=150),
        ),
    ]
