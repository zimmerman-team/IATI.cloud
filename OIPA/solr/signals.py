from django.db.models import signals
from django.dispatch import receiver

from iati.models import Activity, Budget, Result
from iati.transaction.models import Transaction
from iati_synchroniser.models import Dataset, DatasetNote
from solr.activity.tasks import ActivityTaskIndexing
from solr.budget.tasks import BudgetTaskIndexing
from solr.dataset.tasks import DatasetTaskIndexing
from solr.datasetnote.tasks import DatasetNoteTaskIndexing
from solr.result.tasks import ResultTaskIndexing
from solr.transaction.tasks import TransactionTaskIndexing


@receiver(signals.post_save, sender=Dataset)
def dataset_post_save(sender, instance, **kwargs):
    DatasetTaskIndexing(instance=instance).run()


@receiver(signals.post_save, sender=DatasetNote)
def dataset_note_post_save(sender, instance, **kwargs):
    DatasetNoteTaskIndexing(instance=instance).run()


@receiver(signals.pre_delete, sender=Activity)
def activity_pre_delete(sender, instance, **kwargs):
    ActivityTaskIndexing(instance=instance).delete()


@receiver(signals.pre_delete, sender=Budget)
def budget_pre_delete(sender, instance, **kwargs):
    BudgetTaskIndexing(instance=instance).delete()


@receiver(signals.pre_delete, sender=Result)
def result_pre_delete(sender, instance, **kwargs):
    ResultTaskIndexing(instance=instance).delete()


@receiver(signals.pre_delete, sender=Transaction)
def transaction_pre_delete(sender, instance, **kwargs):
    TransactionTaskIndexing(instance=instance).delete()


@receiver(signals.pre_delete, sender=Dataset)
def dataset_pre_delete(sender, instance, **kwargs):
    DatasetTaskIndexing(instance=instance).delete()


@receiver(signals.pre_delete, sender=DatasetNote)
def dataset_note_pre_delete(sender, instance, **kwargs):
    DatasetNoteTaskIndexing(instance=instance).delete()
