# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.db.models import Count
from django.contrib.contenttypes.management import update_contenttypes
import django.db.models.deletion


def remove_duplicate_documentlinktitles(apps, schema_editor):
    """
    document link should have 1 title max, making it a OneToOnefield
    """
    update_contenttypes(apps.get_app_config('iati'), interactive=False) # make sure all content types exist

    try: # don't run on first migration
        DocumentLinkTitle = apps.get_model('iati', 'DocumentLinkTitle')
    except:
        return

    for document_link in DocumentLinkTitle.objects.values('document_link_id').annotate(id_count=Count('document_link')).filter(id_count__gte=2):
        dlts = DocumentLinkTitle.objects.filter(document_link_id=document_link.get('document_link_id'))
        counter = 0
        for dlt in dlts:
            if counter > 0:
                dlt.delete()
            counter += 1

def reverse(apps, schema_editor):
    """
    Impossible
    """
    return

class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0046_auto_20160616_0152'),
    ]

    operations = [
        migrations.RunPython(remove_duplicate_documentlinktitles, reverse),
        migrations.AlterField(
            model_name='documentlinktitle',
            name='document_link',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='iati.DocumentLink'),
        ),
    ]
