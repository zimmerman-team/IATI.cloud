# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations, transaction

from django.apps import apps

from django.contrib.contenttypes.models import ContentType

@transaction.atomic
def get_name_from_narrative(apps, schema_editor):
    APOContentType = ContentType.objects.get(model='activityparticipatingorganisation')

    APO = apps.get_model('iati', 'ActivityParticipatingOrganisation')
    Narrative = apps.get_model('iati', 'Narrative')
    for item in APO.objects.all():
        narrative = Narrative.objects.filter(related_content_type_id=APOContentType.id, related_object_id=item.id)
        if narrative and narrative[0] and narrative[0].content:
            item.primary_name = narrative[0].content
            item.save()
        else: 
            item.primary_name = item.normalized_ref
            item.save()

class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0006_auto_20151125_1700'),
    ]

    operations = [
        migrations.AddField(
            model_name='activityparticipatingorganisation',
            name='primary_name',
            field=models.TextField(default='test'),
            preserve_default=False,
        ),
        migrations.RunPython(get_name_from_narrative),
        # migrations.AlterUniqueTogether(
        #     name='activityparticipatingorganisation',
        #     unique_together=set([('normalized_ref', 'primary_name')]),
        # ),
    ]
