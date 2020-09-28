from django.db.models import signals
from django.dispatch import receiver

from geodata.models import Country, Region
from iati.models import Activity, ActivitySector, Budget
from iati.transaction.models import Transaction, TransactionSector
from iati_organisation.models import Organisation
from iati_synchroniser.models import Dataset, Publisher
from solr.activity.tasks import ActivityTaskIndexing
from solr.activity_sector.tasks import ActivitySectorTaskIndexing
from solr.budget.tasks import BudgetTaskIndexing
from solr.codelists.country.tasks import CodeListCountryTaskIndexing
from solr.codelists.region.tasks import CodeListRegionTaskIndexing
from solr.dataset.tasks import DatasetTaskIndexing
from solr.organisation.tasks import OrganisationTaskIndexing
from solr.publisher.tasks import PublisherTaskIndexing
from solr.transaction.tasks import TransactionTaskIndexing
from solr.transaction_sector.tasks import TransactionSectorTaskIndexing


@receiver(signals.post_save, sender=Dataset)
def dataset_post_save(sender, instance, **kwargs):
    DatasetTaskIndexing(instance=instance).run()


@receiver(signals.post_save, sender=Publisher)
def publisher_post_save(sender, instance, **kwargs):
    PublisherTaskIndexing(instance=instance).run()


@receiver(signals.post_save, sender=Organisation)
def organisation_post_save(sender, instance, **kwargs):
    OrganisationTaskIndexing(instance=instance).run()


@receiver(signals.post_save, sender=Country)
def code_list_country_post_save(sender, instance, **kwargs):
    CodeListCountryTaskIndexing(instance=instance).run()


@receiver(signals.post_save, sender=Region)
def code_list_region_post_save(sender, instance, **kwargs):
    CodeListRegionTaskIndexing(instance=instance).run()


# @receiver(signals.post_save, sender=Activity)
# def activity_post_save(sender, instance, **kwargs):
#     ActivityTaskIndexing(instance=instance, related=True).run()


@receiver(signals.pre_delete, sender=Dataset)
def dataset_pre_delete(sender, instance, **kwargs):
    DatasetTaskIndexing(instance=instance).delete()


@receiver(signals.pre_delete, sender=Publisher)
def publisher_pre_delete(sender, instance, **kwargs):
    PublisherTaskIndexing(instance=instance).delete()


@receiver(signals.pre_delete, sender=Organisation)
def organisation_pre_delete(sender, instance, **kwargs):
    OrganisationTaskIndexing(instance=instance).delete()


@receiver(signals.pre_delete, sender=Country)
def code_list_country_pre_delete(sender, instance, **kwargs):
    CodeListCountryTaskIndexing(instance=instance).delete()


@receiver(signals.pre_delete, sender=Region)
def code_list_region_pre_delete(sender, instance, **kwargs):
    CodeListRegionTaskIndexing(instance=instance).delete()


@receiver(signals.pre_delete, sender=Activity)
def activity_pre_delete(sender, instance, **kwargs):
    ActivityTaskIndexing(instance=instance).delete()


@receiver(signals.pre_delete, sender=Budget)
def budget_pre_delete(sender, instance, **kwargs):
    BudgetTaskIndexing(instance=instance).delete()


@receiver(signals.pre_delete, sender=Transaction)
def transaction_pre_delete(sender, instance, **kwargs):
    TransactionTaskIndexing(instance=instance).delete()


# @receiver(signals.pre_delete, sender=ActivitySector)
# def activity_sector_pre_delete(sender, instance, **kwargs):
#     ActivitySectorTaskIndexing(instance=instance).delete()
#
#
# @receiver(signals.pre_delete, sender=TransactionSector)
# def transaction_sector_pre_delete(sender, instance, **kwargs):
#     TransactionSectorTaskIndexing(instance=instance).delete()
