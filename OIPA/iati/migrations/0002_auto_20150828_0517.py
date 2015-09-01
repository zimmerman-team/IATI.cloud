# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactinfo',
            name='contact_type',
            field=models.ForeignKey(default=None, blank=True, to='iati.ContactType', null=True),
        ),
        migrations.AlterField(
            model_name='contactinfo',
            name='email',
            field=models.TextField(default=b'', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='contactinfo',
            name='job_title',
            field=models.CharField(default=b'', max_length=150, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='contactinfo',
            name='mailing_address',
            field=models.TextField(default=b'', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='contactinfo',
            name='organisation',
            field=models.CharField(default=b'', max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='contactinfo',
            name='person_name',
            field=models.CharField(default=b'', max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='contactinfo',
            name='telephone',
            field=models.CharField(default=b'', max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='contactinfo',
            name='website',
            field=models.CharField(default=b'', max_length=255, null=True, blank=True),
        ),
    ]
