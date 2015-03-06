# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ParseLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file_name', models.CharField(max_length=256)),
                ('location', models.CharField(max_length=512)),
                ('error_time', models.DateTimeField()),
                ('error_text', models.TextField()),
                ('error_hint', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
