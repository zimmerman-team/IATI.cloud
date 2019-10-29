from django.db.models import signals
from django.dispatch import receiver

from iati.models import Activity
from iati.transaction.models import Transaction

from solr.activity.tasks import ActivityTaskIndexing
from solr.transaction.tasks import TransactionTaskIndexing


@receiver(signals.pre_delete, sender=Activity)
def activity_pre_delete(sender, instance, **kwargs):
    ActivityTaskIndexing(activity=instance).delete()


@receiver(signals.pre_delete, sender=Transaction)
def transaction_pre_delete(sender, instance, **kwargs):
    TransactionTaskIndexing(transaction=instance).delete()
