from django.db import models
from geodata.models import Country, Region
from iati_vocabulary.models import RegionVocabulary, SectorVocabulary
from iati_codelists.models import AidType, DescriptionType, DisbursementChannel, FinanceType, FlowType, TiedStatus, Currency, Sector, TransactionType
from iati.models import Organisation, Activity, Narrative
from django.contrib.contenttypes.fields import GenericRelation

class TransactionProvider(models.Model):
    ref = models.CharField(max_length=250)
    normalized_ref = models.CharField(max_length=120, default="")

    organisation = models.ForeignKey(
        Organisation,
        related_name="transaction_providing_organisation",
        null=True,
        default=None)
    provider_activity = models.ForeignKey(
        Activity,
        related_name="transaction_provider_activity",
        db_constraint=False,
        null=True,
        default=None)
    provider_activity_ref = models.CharField(max_length=200, default="")

    narratives = GenericRelation(Narrative)

class TransactionReceiver(models.Model):
    ref = models.CharField(max_length=250)
    normalized_ref = models.CharField(max_length=120, default="")

    organisation = models.ForeignKey(
        'Organisation',
        related_name="transaction_receiving_organisation",
        null=True,
        default=None)
    receiver_activity = models.ForeignKey(
        Activity,
        related_name="transaction_receiver_activity",
        db_constraint=False,
        null=True,
        default=None)
    receiver_activity_ref = models.CharField(max_length=200, default="")

    narratives = GenericRelation(Narrative)

class Transaction(models.Model):
    activity = models.ForeignKey(Activity)
    aid_type = models.ForeignKey(AidType, null=True, default=None)
    description = models.TextField(null=True, default=None)
    description_type = models.ForeignKey(
        DescriptionType,
        null=True,
        default=None)
    disbursement_channel = models.ForeignKey(
        DisbursementChannel,
        null=True,
        default=None)
    finance_type = models.ForeignKey(FinanceType, null=True, default=None)
    flow_type = models.ForeignKey(FlowType, null=True, default=None)

    provider_organisation = models.OneToOneField(
        TransactionProvider,
        related_name="transaction_provider_organisation",
        null=True)
    receiver_organisation = models.OneToOneField(
        TransactionReceiver,
        related_name="transaction_receiver_organisation",
        null=True)

    tied_status = models.ForeignKey(TiedStatus, null=True, default=None)
    transaction_date = models.DateField(null=True, default=None)
    transaction_type = models.ForeignKey(
        TransactionType,
        null=True,
        default=None)
    value_date = models.DateField(null=True, default=None)
    value = models.DecimalField(max_digits=15, decimal_places=2)
    value_string = models.CharField(max_length=50)
    currency = models.ForeignKey(Currency, null=True, default=None)
    ref = models.CharField(max_length=255, null=True, default="")
    recipient_region = models.ForeignKey(Region, null=True)
    recipient_region_vocabulary = models.ForeignKey(RegionVocabulary, default=1)
    recipient_country = models.ForeignKey(Country, null=True, default=None)

    def __unicode__(self,):
        return "%s: %s - %s" % (self.activity,
                                self.transaction_type,
                                self.transaction_date)

class TransactionSector(models.Model):
    transaction = models.ForeignKey(Transaction)
    sector = models.ForeignKey(Sector)
    vocabulary = models.ForeignKey(SectorVocabulary)

    def __unicode__(self,):
        return "%s - %s" % (self.transaction.id, self.sector)

class TransactionRecipientCountry(models.Model):
    transaction = models.ForeignKey(Transaction)
    country = models.ForeignKey(Country)

    def __unicode__(self,):
        return "%s - %s" % (self.transaction.id, self.country)

class TransactionRecipientRegion(models.Model):
    transaction = models.ForeignKey(Transaction)
    region = models.ForeignKey(Region)
    region_vocabulary = models.ForeignKey(RegionVocabulary, default=1)

    def __unicode__(self,):
        return "%s - %s" % (self.transaction.id, self.region)

class TransactionDescription(models.Model):
    transaction = models.ForeignKey(Transaction)
    narratives = GenericRelation(Narrative)


