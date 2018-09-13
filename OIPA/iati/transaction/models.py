from decimal import Decimal

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from geodata.models import Country, Region
from iati.models import Activity, Narrative
from iati.transaction.transaction_manager import TransactionQuerySet
from iati_codelists.models import (
    AidType, Currency, DisbursementChannel, FinanceType, FlowType, Sector,
    TiedStatus, TransactionType
)
from iati_organisation.models import Organisation, OrganisationType
from iati_vocabulary.models import RegionVocabulary, SectorVocabulary, \
    AidTypeVocabulary


class Transaction(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)

    ref = models.CharField(max_length=255, null=True, blank=True, default="")

    transaction_type = models.ForeignKey(
        TransactionType, on_delete=models.CASCADE)
    transaction_date = models.DateField(db_index=True)

    value = models.DecimalField(max_digits=15, decimal_places=2)
    value_string = models.CharField(max_length=50)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    value_date = models.DateField()

    humanitarian = models.NullBooleanField(null=True, blank=True)

    xdr_value = models.DecimalField(
        max_digits=20, decimal_places=7, default=Decimal(0))
    usd_value = models.DecimalField(
        max_digits=20, decimal_places=7, default=Decimal(0))
    eur_value = models.DecimalField(
        max_digits=20, decimal_places=7, default=Decimal(0))
    gbp_value = models.DecimalField(
        max_digits=20, decimal_places=7, default=Decimal(0))
    jpy_value = models.DecimalField(
        max_digits=20, decimal_places=7, default=Decimal(0))
    cad_value = models.DecimalField(
        max_digits=20, decimal_places=7, default=Decimal(0))

    disbursement_channel = models.ForeignKey(
        DisbursementChannel,
        null=True,
        blank=True,
        default=None, on_delete=models.CASCADE)

    flow_type = models.ForeignKey(
        FlowType, null=True, blank=True,
        default=None, on_delete=models.CASCADE)
    finance_type = models.ForeignKey(
        FinanceType, null=True, blank=True,
        default=None, on_delete=models.CASCADE)
    tied_status = models.ForeignKey(
        TiedStatus, null=True, blank=True,
        default=None, on_delete=models.CASCADE)

    objects = TransactionQuerySet.as_manager()

    def __unicode__(self, ):
        return "value: %s - transaction date: %s - type: %s" % (
            self.value,
            self.transaction_date,
            self.transaction_type,)

    def get_publisher(self):
        return self.activity.publisher


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

    type = models.ForeignKey(
        OrganisationType,
        null=True,
        default=None,
        blank=True, on_delete=models.CASCADE)

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
        related_name="provider_organisation", on_delete=models.CASCADE)

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

    def get_publisher(self):
        return self.transaction.activity.publisher


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

    type = models.ForeignKey(
        OrganisationType,
        null=True,
        default=None,
        blank=True, on_delete=models.CASCADE)

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
        related_name="receiver_organisation", on_delete=models.CASCADE)

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

    def get_publisher(self):
        return self.transaction.activity.publisher


class TransactionDescription(models.Model):
    transaction = models.OneToOneField(
        Transaction,
        related_name="description", on_delete=models.CASCADE)

    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    def get_publisher(self):
        return self.transaction.activity.publisher


class TransactionSector(models.Model):
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE
    )

    reported_transaction = models.OneToOneField(
        Transaction,
        related_name="transaction_sector",
        null=True, on_delete=models.CASCADE
    )

    sector = models.ForeignKey(
        Sector,
        on_delete=models.CASCADE)

    vocabulary = models.ForeignKey(
        SectorVocabulary,
        null=True,
        blank=True,
        default=None,
        on_delete=models.CASCADE)

    vocabulary_uri = models.URLField(null=True, blank=True)

    reported_on_transaction = models.BooleanField(default=True)

    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2)

    def __unicode__(self, ):
        return "%s - %s" % (self.transaction.id, self.sector)

    def get_publisher(self):
        return self.transaction.activity.publisher


class TransactionRecipientCountry(models.Model):
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        # related_name="recipient_country"
    )

    reported_transaction = models.OneToOneField(
        Transaction,
        related_name="transaction_recipient_country",
        null=True, on_delete=models.CASCADE
    )

    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE)

    reported_on_transaction = models.BooleanField(default=True)

    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2)

    def __unicode__(self, ):
        return "%s - %s" % (self.transaction.id, self.country)

    def get_publisher(self):
        return self.transaction.activity.publisher


class TransactionRecipientRegion(models.Model):
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        # related_name="recipient_region"
    )

    reported_transaction = models.OneToOneField(
        Transaction,
        related_name="transaction_recipient_region",
        null=True, on_delete=models.CASCADE
    )

    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE)

    vocabulary = models.ForeignKey(
        RegionVocabulary,
        null=True,
        blank=True,
        default=1,
        on_delete=models.CASCADE)

    vocabulary_uri = models.URLField(null=True, blank=True)

    reported_on_transaction = models.BooleanField(default=True)

    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2)

    def __unicode__(self, ):
        return "%s - %s" % (self.transaction.id, self.region)

    def get_publisher(self):
        return self.transaction.activity.publisher


class TransactionAidType(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    aid_type = models.ForeignKey(AidType, on_delete=models.CASCADE)

    def __string__(self, ):
        return "%s - %s" % (self.transaction.id, self.aid_type.code)


class TransactionAidTypeVocabulary(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    aid_type_vocabulary = models.ForeignKey(
        AidTypeVocabulary, on_delete=models.CASCADE)

    def __string__(self, ):
        return "%s - %s" % (self.transaction.id, self.aid_type.code)

