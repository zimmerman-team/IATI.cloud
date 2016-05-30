from decimal import Decimal

from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from iati.transaction.transaction_manager import TransactionQuerySet
from geodata.models import Country
from geodata.models import Region
from iati_vocabulary.models import RegionVocabulary
from iati_vocabulary.models import SectorVocabulary
from iati_codelists.models import AidType
from iati_codelists.models import DisbursementChannel
from iati_codelists.models import FinanceType
from iati_codelists.models import FlowType
from iati_codelists.models import TiedStatus
from iati_codelists.models import Currency
from iati_codelists.models import Sector
from iati_codelists.models import TransactionType
from iati_organisation.models import Organisation
from iati.models import Activity
from iati.models import Narrative


class Transaction(models.Model):
    activity = models.ForeignKey(Activity)

    ref = models.CharField(max_length=255, null=True, blank=True, default="")

    transaction_type = models.ForeignKey(
        TransactionType)
    transaction_date = models.DateField(db_index=True)

    value = models.DecimalField(max_digits=15, decimal_places=2)
    value_string = models.CharField(max_length=50)
    currency = models.ForeignKey(Currency)
    value_date = models.DateField()

    xdr_value = models.DecimalField(max_digits=20, decimal_places=7, default=Decimal(0))
    usd_value = models.DecimalField(max_digits=20, decimal_places=7, default=Decimal(0))
    eur_value = models.DecimalField(max_digits=20, decimal_places=7, default=Decimal(0))
    gbp_value = models.DecimalField(max_digits=20, decimal_places=7, default=Decimal(0))
    jpy_value = models.DecimalField(max_digits=20, decimal_places=7, default=Decimal(0))
    cad_value = models.DecimalField(max_digits=20, decimal_places=7, default=Decimal(0))

    disbursement_channel = models.ForeignKey(
        DisbursementChannel,
        null=True,
        blank=True,
        default=None
    )

    flow_type = models.ForeignKey(FlowType, null=True, blank=True, default=None)
    finance_type = models.ForeignKey(FinanceType, null=True, blank=True, default=None)
    aid_type = models.ForeignKey(AidType, null=True, blank=True, default=None)
    tied_status = models.ForeignKey(TiedStatus, null=True, blank=True, default=None)

    objects = TransactionQuerySet.as_manager()

    def __unicode__(self, ):
        return "value: %s - transaction date: %s - type: %s" % (
            self.value,
            self.transaction_date,
            self.transaction_type,)


class TransactionProvider(models.Model):
    ref = models.CharField(blank=True, default="", max_length=250)
    normalized_ref = models.CharField(max_length=120, default="")

    organisation = models.ForeignKey(
        Organisation,
        related_name="transaction_providing_organisation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None)
    provider_activity = models.ForeignKey(
        Activity,
        related_name="transaction_provider_activity",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None)
    provider_activity_ref = models.CharField(
        db_index=True,
        max_length=200,
        null=True,
        blank=True,
        default="",
        verbose_name='provider-activity-id')

    transaction = models.OneToOneField(
        Transaction,
        related_name="provider_organisation")

    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    # first narrative
    primary_name = models.CharField(
        max_length=250,
        null=False,
        blank=True,
        default="",
        db_index=True)

    def __unicode__(self, ):
        return "%s - %s" % (self.ref,
                            self.provider_activity_ref,)


class TransactionReceiver(models.Model):
    ref = models.CharField(blank=True, default="", max_length=250)
    normalized_ref = models.CharField(max_length=120, default="")

    organisation = models.ForeignKey(
        Organisation,
        related_name="transaction_receiving_organisation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None)
    receiver_activity = models.ForeignKey(
        Activity,
        related_name="transaction_receiver_activity",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None)
    receiver_activity_ref = models.CharField(
        db_index=True,
        max_length=200,
        null=True,
        blank=True,
        default="",
        verbose_name='receiver-activity-id')

    transaction = models.OneToOneField(
        Transaction,
        related_name="receiver_organisation")

    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    # first narrative
    primary_name = models.CharField(
        max_length=250,
        null=False,
        blank=True,
        default="",
        db_index=True)

    def __unicode__(self, ):
        return "%s - %s" % (self.ref,
                            self.receiver_activity_ref,)


class TransactionDescription(models.Model):
    transaction = models.OneToOneField(
        Transaction,
        related_name="description")

    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')


class TransactionSector(models.Model):
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE)
    
    sector = models.ForeignKey(
        Sector,
        on_delete=models.CASCADE)

    vocabulary = models.ForeignKey(
        SectorVocabulary,
        null=True,
        blank=True,
        default=None,
        on_delete=models.CASCADE)

    reported_on_transaction = models.BooleanField(default=True)

    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2)

    def __unicode__(self, ):
        return "%s - %s" % (self.transaction.id, self.sector)


class TransactionRecipientCountry(models.Model):
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE)
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE)

    reported_on_transaction = models.BooleanField(default=True)

    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2)

    def __unicode__(self, ):
        return "%s - %s" % (self.transaction.id, self.country)


class TransactionRecipientRegion(models.Model):
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE)
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE)

    vocabulary = models.ForeignKey(
        RegionVocabulary,
        null=True, 
        blank=True, 
        default=1,
        on_delete=models.CASCADE)

    reported_on_transaction = models.BooleanField(default=True)

    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2)

    def __unicode__(self, ):
        return "%s - %s" % (self.transaction.id, self.region)

