# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0002_relatedactivity_related_activity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='legacydata',
            name='name',
            field=models.CharField(max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='narrative',
            name='iati_identifier',
            field=models.CharField(max_length=100, null=True, verbose_name=b'iati_identifier'),
        ),
        migrations.AlterField(
            model_name='narrative',
            name='object_id',
            field=models.CharField(max_length=100, null=True, verbose_name=b'related object'),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='abbreviation',
            field=models.CharField(default=b'', max_length=120),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='code',
            field=models.CharField(max_length=120, serialize=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='original_ref',
            field=models.CharField(default=b'', max_length=120),
        ),
    ]
