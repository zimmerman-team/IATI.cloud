from django.db.models import signals
from django.dispatch import receiver

from iati.models import Activity
from solr.models import ActivityDelete


@receiver(signals.pre_delete, sender=Activity)
def indicator_pre_delete(sender, instance, **kwargs):
    activity_delete = ActivityDelete()
    activity_delete.activity_id = instance.id
    activity_delete.save()
