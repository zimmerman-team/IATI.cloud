from django.db.models import signals
from django.dispatch import receiver

from iati.models import Activity, Result
from iati.transaction.models import Transaction
from solr.models import ActivityDelete, ResultDelete


@receiver(signals.pre_delete, sender=Activity)
def activity_pre_delete(sender, instance, **kwargs):
    activity_delete = ActivityDelete()
    activity_delete.activity_id = instance.id
    activity_delete.save()


@receiver(signals.pre_delete, sender=Result)
def result_pre_delete(sender, instance, **kwargs):
    result_delete = ResultDelete()
    result_delete.activity_id = instance.id
    result_delete.save()


@receiver(signals.pre_delete, sender=Transaction)
def transaction_pre_delete(sender, instance, **kwargs):
    transaction_delete = Transaction()
    transaction_delete.activity_id = instance.id
    transaction_delete.save()
