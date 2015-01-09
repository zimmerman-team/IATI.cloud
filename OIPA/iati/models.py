from django.db import models
from geodata.models import Country, Region
from activity_manager import ActivityQuerySet
from django.contrib.gis.geos import Point
from iati.transaction.models import Transaction
from iati.transaction.models import TransactionType


class ActivityDateType(models.Model):
    code = models.CharField(primary_key=True, max_length=20)
    name = models.CharField(max_length=200)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class ActivityStatus(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    language = models.CharField(max_length=2)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class AidTypeCategory(models.Model):
    code = models.CharField(primary_key=True, max_length=3)
    name = models.CharField(max_length=200)
    description = models.TextField()

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class AidType(models.Model):
    code = models.CharField(primary_key=True, max_length=3)
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(AidTypeCategory)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class BudgetType(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    language = models.CharField(max_length=2)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class CollaborationType(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    language = models.CharField(max_length=2)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class ConditionType(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=40)
    language = models.CharField(max_length=2)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class Currency(models.Model):
    code = models.CharField(primary_key=True, max_length=3)
    name = models.CharField(max_length=100)
    language = models.CharField(max_length=2)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class DescriptionType(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class DisbursementChannel(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.TextField()

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class DocumentCategoryCategory(models.Model):
    code = models.CharField(primary_key=True, max_length=3)
    name = models.CharField(max_length=100)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class DocumentCategory(models.Model):
    code = models.CharField(primary_key=True, max_length=3)
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey(DocumentCategoryCategory)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class FileFormat(models.Model):
    code = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=100)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class FinanceTypeCategory(models.Model):
    code = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class FinanceType(models.Model):
    code = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=220)
    category = models.ForeignKey(FinanceTypeCategory)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class FlowType(models.Model):
    code = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=150)
    description = models.TextField()

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class GazetteerAgency(models.Model):
    code = models.CharField(primary_key=True, max_length=3)
    name = models.CharField(max_length=80)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class GeographicalPrecision(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=80)
    description = models.TextField()

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class GeographicLocationClass(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=200)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class Language(models.Model):
    code = models.CharField(primary_key=True, max_length=2)
    name = models.CharField(max_length=80)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class LocationTypeCategory(models.Model):
    code = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=100)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class LocationType(models.Model):
    code = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, default=None)
    category = models.ForeignKey(LocationTypeCategory)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class OrganisationIdentifier(models.Model):
    code = models.CharField(primary_key=True, max_length=20)
    abbreviation = models.CharField(max_length=30, default=None, null=True)
    name = models.CharField(max_length=250, default=None, null=True)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class OrganisationRole(models.Model):
    code = models.CharField(primary_key=True, max_length=20)
    name = models.CharField(max_length=20)
    description = models.TextField()

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class OrganisationType(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=50)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class PolicyMarker(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=200)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class PolicySignificance(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class PublisherType(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=50)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class RelatedActivityType(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    description = models.TextField()

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class ResultType(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=30)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class SectorCategory(models.Model):
    code = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class Sector(models.Model):
    code = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey(SectorCategory, null=True, default=None)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class TiedStatus(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=40)
    description = models.TextField()

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class ValueType(models.Model):
    code = models.CharField(primary_key=True, max_length=2)
    name = models.CharField(max_length=40)
    description = models.TextField()

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class VerificationStatus(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=20)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class Vocabulary(models.Model):
    code = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=140)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class ActivityScope(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class AidTypeFlag(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class BudgetIdentifier(models.Model):
    code = models.CharField(primary_key=True, max_length=20)
    name = models.CharField(max_length=160)
    category = models.CharField(max_length=120)
    sector = models.CharField(max_length=100)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class BudgetIdentifierSectorCategory(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=160)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class BudgetIdentifierSector(models.Model):
    code = models.CharField(primary_key=True, max_length=20)
    name = models.CharField(max_length=160)
    category = models.ForeignKey(BudgetIdentifierSectorCategory)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class BudgetIdentifierVocabulary(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class ContactType(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=40)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class LoanRepaymentPeriod(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=20)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class LoanRepaymentType(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=40)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class RegionVocabulary(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=20)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class Organisation(models.Model):
    code = models.CharField(primary_key=True, max_length=80)
    abbreviation = models.CharField(max_length=80, null=True, default=None)
    type = models.ForeignKey(OrganisationType, null=True, default=None)
    reported_by_organisation = models.CharField(
        max_length=100, null=True, default=None)
    name = models.CharField(max_length=250, null=True, default=None)
    original_ref = models.CharField(max_length=80, null=True, default=None)

    def __unicode__(self):
        return self.name

    def total_activities(self):
        return self.activity_set.count()


class Activity(models.Model):
    hierarchy_choices = (
        (1, u"Parent"),
        (2, u"Child"),
    )

    id = models.CharField(primary_key=True, max_length=150)
    iati_identifier = models.CharField(max_length=150)
    default_currency = models.ForeignKey(
        Currency,
        null=True,
        default=None,
        related_name="default_currency")
    hierarchy = models.SmallIntegerField(
        choices=hierarchy_choices,
        default=1,
        null=True)
    last_updated_datetime = models.CharField(
        max_length=100,
        null=True,
        default=None)
    linked_data_uri = models.CharField(max_length=100, blank=True, null=True)
    reporting_organisation = models.ForeignKey(
        Organisation,
        null=True,
        default=None,
        related_name="activity_reporting_organisation")
    secondary_publisher = models.BooleanField(default=False)
    activity_status = models.ForeignKey(
        ActivityStatus,
        null=True,
        default=None)

    start_planned = models.DateField(null=True, blank=True, default=None)
    end_planned = models.DateField(null=True, blank=True, default=None)
    start_actual = models.DateField(null=True, blank=True, default=None)
    end_actual = models.DateField(null=True, blank=True, default=None)

    participating_organisation = models.ManyToManyField(
        Organisation,
        through="ActivityParticipatingOrganisation")
    policy_marker = models.ManyToManyField(
        PolicyMarker,
        through="ActivityPolicyMarker")
    sector = models.ManyToManyField(Sector, through="ActivitySector")
    recipient_country = models.ManyToManyField(
        Country,
        through="ActivityRecipientCountry")
    recipient_region = models.ManyToManyField(
        Region,
        through="ActivityRecipientRegion")

    collaboration_type = models.ForeignKey(
        CollaborationType,
        null=True,
        default=None)
    default_flow_type = models.ForeignKey(FlowType, null=True, default=None)
    default_aid_type = models.ForeignKey(AidType, null=True, default=None)
    default_finance_type = models.ForeignKey(
        FinanceType,
        null=True,
        default=None)
    default_tied_status = models.ForeignKey(
        TiedStatus,
        null=True,
        default=None)
    xml_source_ref = models.CharField(null=True, max_length=200)
    total_budget_currency = models.ForeignKey(
        Currency,
        null=True,
        default=None,
        related_name="total_budget_currency")
    total_budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        default=None,
        db_index=True)

    capital_spend = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        default=None)
    scope = models.ForeignKey(ActivityScope, null=True, default=None)
    iati_standard_version = models.CharField(
        max_length=30,
        null=True,
        default=None)

    objects = ActivityQuerySet.as_manager()

    def __unicode__(self):
        return self.id

    class Meta:
        verbose_name_plural = "activities"


class ActivitySearchData(models.Model):
    activity = models.OneToOneField(Activity)
    search_identifier = models.CharField(db_index=True, max_length=150)
    search_description = models.TextField(max_length=80000)
    search_title = models.TextField(max_length=80000)
    search_country_name = models.TextField(max_length=80000)
    search_region_name = models.TextField(max_length=80000)
    search_sector_name = models.TextField(max_length=80000)
    search_participating_organisation_name = models.TextField(max_length=80000)
    search_reporting_organisation_name = models.TextField(max_length=80000)
    search_documentlink_title = models.TextField(max_length=80000)


class ActivityParticipatingOrganisation(models.Model):
    activity = models.ForeignKey(
        Activity,
        related_name="participating_organisations")
    organisation = models.ForeignKey(Organisation, null=True, default=None)
    role = models.ForeignKey(OrganisationRole, null=True, default=None)
    name = models.TextField(null=True, default=None)

    def __unicode__(self,):
        return "%s: %s - %s" % (self.activity, self.organisation, self.name)


class ActivityPolicyMarker(models.Model):
    policy_marker = models.ForeignKey(PolicyMarker, null=True, default=None)
    alt_policy_marker = models.CharField(
        max_length=200,
        null=True,
        default=None)
    activity = models.ForeignKey(Activity)
    vocabulary = models.ForeignKey(Vocabulary, null=True, default=None)
    policy_significance = models.ForeignKey(
        PolicySignificance,
        null=True,
        default=None)

    def __unicode__(self,):
        return "%s - %s" % (self.activity, self.policy_marker)


class ActivitySector(models.Model):
    activity = models.ForeignKey(Activity)
    sector = models.ForeignKey(Sector, null=True, default=None)
    alt_sector_name = models.CharField(max_length=200, null=True, default=None)
    vocabulary = models.ForeignKey(Vocabulary, null=True, default=None)
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        default=None)

    def __unicode__(self,):
        return "%s - %s" % (self.activity, self.sector)


class ActivityRecipientCountry(models.Model):
    activity = models.ForeignKey(Activity)
    country = models.ForeignKey(Country)
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        default=None)

    def __unicode__(self,):
        return "%s - %s" % (self.activity, self.country)


class CountryBudgetItem(models.Model):
    activity = models.ForeignKey(Activity)
    vocabulary = models.ForeignKey(BudgetIdentifierVocabulary, null=True)
    vocabulary_text = models.CharField(max_length=255, null=True, default=None)
    code = models.CharField(max_length=50, null=True, default=None)
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        default=None)
    description = models.TextField(null=True, default=None)


class ActivityRecipientRegion(models.Model):
    activity = models.ForeignKey(Activity)
    region = models.ForeignKey(Region)
    region_vocabulary = models.ForeignKey(RegionVocabulary, default=1)
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        default=None)

    def __unicode__(self,):
        return "%s - %s" % (self.activity, self.region)


class OtherIdentifier(models.Model):
    activity = models.ForeignKey(Activity)
    owner_ref = models.CharField(max_length=100, null=True, default=None)
    owner_name = models.CharField(max_length=100, null=True, default=None)
    identifier = models.CharField(max_length=100)

    def __unicode__(self,):
        return "%s - %s" % (self.activity, self.identifier)


class ActivityWebsite(models.Model):
    activity = models.ForeignKey(Activity)
    url = models.CharField(max_length=150)

    def __unicode__(self,):
        return "%s - %s" % (self.activity, self.url)


#   Class not truly correct, attributes fully open
class ContactInfo(models.Model):
    activity = models.ForeignKey(Activity)
    person_name = models.CharField(max_length=100, null=True, default=None)
    organisation = models.CharField(max_length=100, null=True, default=None)
    telephone = models.CharField(max_length=100, null=True, default=None)
    email = models.TextField(null=True, default=None)
    mailing_address = models.TextField(null=True, default=None)
    website = models.CharField(max_length=255, null=True, default=None)
    contact_type = models.ForeignKey(ContactType, null=True, default=None)
    job_title = models.CharField(max_length=150, null=True, default=None)

    def __unicode__(self,):
        return "%s - %s" % (self.activity, self.person_name)


# class transaction_description(models.Model):
#     transaction = models.ForeignKey(transaction)
#     type = models.ForeignKey(description_type, null=True, default=None)
#     language = models.ForeignKey(language, null=True, default=None)
#     description = models.TextField(null=True, default=None)
#
#     def __unicode__(self,):
#         return "%s - %s" % (self.code, self.name)


class PlannedDisbursement(models.Model):
    activity = models.ForeignKey(Activity)
    period_start = models.CharField(max_length=100, null=True, default=None)
    period_end = models.CharField(max_length=100, null=True, default=None)
    value_date = models.DateField(null=True)
    value = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.ForeignKey(Currency, null=True, default=None)
    updated = models.DateField(null=True, default=None)

    def __unicode__(self,):
        return "%s - %s" % (self.activity, self.period_start)


class RelatedActivity(models.Model):
    current_activity = models.ForeignKey(
        Activity,
        related_name="current_activity")
    type = models.ForeignKey(
        RelatedActivityType,
        max_length=200,
        null=True,
        default=None)
    ref = models.CharField(max_length=200, null=True, default=None)
    text = models.TextField(null=True, default=None)

    def __unicode__(self,):
        return "%s - %s" % (self.current_activity, self.type)


class DocumentLink(models.Model):
    activity = models.ForeignKey(Activity)
    url = models.TextField(max_length=500)
    file_format = models.ForeignKey(FileFormat, null=True, default=None)
    document_category = models.ForeignKey(
        DocumentCategory,
        null=True,
        default=None)
    title = models.CharField(max_length=255, null=True, default=None)

    def __unicode__(self,):
        return "%s - %s" % (self.activity, self.url)


class Result(models.Model):
    activity = models.ForeignKey(Activity)
    result_type = models.ForeignKey(ResultType, null=True, default=None)
    title = models.CharField(max_length=255, null=True, default=None)
    description = models.TextField(null=True, default=None)
    aggregation_status = models.BooleanField(default=False)

    def __unicode__(self,):
        return "%s - %s" % (self.activity, self.title)


class ResultIndicatorMeasure(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=40)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class ResultIndicator(models.Model):
    result = models.ForeignKey(Result)
    title = models.CharField(max_length=200, null=True, default=None)
    description = models.TextField(null=True, default=None)
    baseline_year = models.IntegerField(max_length=4)
    baseline_value = models.CharField(max_length=100)
    comment = models.TextField(null=True, default=None)
    measure = models.ForeignKey(
        ResultIndicatorMeasure,
        null=True,
        default=None)

    def __unicode__(self,):
        return "%s - %s" % (self.result, self.year)


class ResultIndicatorPeriod(models.Model):
    result_indicator = models.ForeignKey(ResultIndicator)
    period_start = models.CharField(max_length=50, null=True, default=None)
    period_end = models.CharField(max_length=50, null=True, default=None)
    planned_disbursement_period_start = models.CharField(
        max_length=50,
        null=True,
        default=None)
    planned_disbursement_period_end = models.CharField(
        max_length=50,
        null=True,
        default=None)
    target = models.CharField(max_length=50, null=True, default=None)
    actual = models.CharField(max_length=50, null=True, default=None)

    def __unicode__(self,):
        return "%s" % (self.result_indicator)


class Title(models.Model):
    activity = models.ForeignKey(Activity)
    title = models.CharField(max_length=255, db_index=True)
    language = models.ForeignKey(Language, null=True, default=None)

    def __unicode__(self,):
        return "%s - %s" % (self.activity, self.title)


class Description(models.Model):
    activity = models.ForeignKey(Activity)
    description = models.TextField(
        null=True,
        default=None,
        db_index=True,
        max_length=40000)
    language = models.ForeignKey(Language, null=True, default=None)
    type = models.ForeignKey(
        DescriptionType,
        related_name="description_type",
        null=True,
        default=None)
    rsr_description_type_id = models.IntegerField(  # remove
        null=True,
        default=None)

    def __unicode__(self,):
        return "%s - %s" % (self.activity, self.type)


class Budget(models.Model):
    activity = models.ForeignKey(Activity)
    type = models.ForeignKey(BudgetType, null=True, default=None)
    period_start = models.CharField(max_length=50, null=True, default=None)
    period_end = models.CharField(max_length=50, null=True, default=None)
    value = models.DecimalField(max_digits=15, decimal_places=2)
    value_date = models.DateField(null=True, default=None)
    currency = models.ForeignKey(Currency, null=True, default=None)

    def __unicode__(self,):
        return "%s - %s" % (self.activity, self.period_start)


class Condition(models.Model):
    activity = models.ForeignKey(Activity)
    text = models.TextField(null=True, default=None)
    type = models.ForeignKey(ConditionType, null=True, default=None)

    def __unicode__(self,):
        return "%s - %s" % (self.activity, self.type)


class GeographicVocabulary(models.Model):
    code = models.CharField(primary_key=True, max_length=20)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, default=None)
    category = models.CharField(max_length=50)
    url = models.TextField(null=True, default=None)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class GeographicLocationReach(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=80)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class OrganisationRegistrationAgency(models.Model):
    code = models.CharField(primary_key=True, max_length=20)
    name = models.CharField(max_length=160)
    description = models.TextField(null=True, default=None)
    category = models.CharField(max_length=10)
    category_name = models.CharField(max_length=120)
    url = models.TextField(null=True, default=None)

    def __unicode__(self,):
        return "%s - %s" % (self.activity, self.type)


class GeographicExactness(models.Model):
    code = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=160)
    description = models.TextField(null=True, default=None)
    category = models.CharField(max_length=50)
    url = models.TextField(null=True, default=None)

    def __unicode__(self,):
        return "%s - %s" % (self.code, self.name)


class Location(models.Model):
    activity = models.ForeignKey(Activity)
    # new in v1.04
    ref = models.CharField(max_length=200, null=True, default=None)
    name = models.TextField(max_length=1000, null=True, default=None)
    # deprecated as of v1.04
    type = models.ForeignKey(
        LocationType,
        null=True,
        default=None,
        related_name="deprecated_location_type")
    type_description = models.CharField(
        max_length=200,
        null=True,
        default=None)
    description = models.TextField(null=True, default=None)
    activity_description = models.TextField(null=True, default=None)
    description_type = models.ForeignKey(
        DescriptionType,
        null=True,
        default=None)
    # deprecated as of v1.04
    adm_country_iso = models.ForeignKey(Country, null=True, default=None)
    # deprecated as of v1.04
    adm_country_adm1 = models.CharField(
        max_length=100,
        null=True,
        default=None)
    # deprecated as of v1.04
    adm_country_adm2 = models.CharField(
        max_length=100,
        null=True,
        default=None)
    # deprecated as of v1.04
    adm_country_name = models.CharField(
        max_length=200,
        null=True,
        default=None)
    # new in v1.04
    adm_code = models.CharField(max_length=255, null=True, default=None)
    # new in v1.04
    adm_vocabulary = models.ForeignKey(
        GeographicVocabulary,
        null=True,
        default=None,
        related_name="administrative_vocabulary")
    # new in v1.04
    adm_level = models.IntegerField(null=True, default=None)
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        default=None)
    # deprecated as of v1.04
    latitude = models.CharField(max_length=70, null=True, default=None)
    # deprecated as of v1.04
    longitude = models.CharField(max_length=70, null=True, default=None)
    precision = models.ForeignKey(
        GeographicalPrecision,
        null=True,
        default=None)
    # deprecated as of v1.04
    gazetteer_entry = models.CharField(max_length=70, null=True, default=None)
    # deprecated as of v1.04
    gazetteer_ref = models.ForeignKey(GazetteerAgency, null=True, default=None)
    # new in v1.04
    location_reach = models.ForeignKey(
        GeographicLocationReach,
        null=True,
        default=None)
    # new in v1.04
    location_id_vocabulary = models.ForeignKey(
        GeographicVocabulary,
        null=True,
        default=None,
        related_name="location_id_vocabulary")
    # new in v1.04
    location_id_code = models.CharField(max_length=255, null=True, default=None)
    # new in v1.04
    point_srs_name = models.CharField(max_length=255, null=True, default=None)
    # new in v1.04
    point_pos = models.CharField(max_length=255, null=True, default=None)
    # new in v1.04
    exactness = models.ForeignKey(GeographicExactness, null=True, default=None)
    # new in v1.04
    feature_designation = models.ForeignKey(
        LocationType,
        null=True,
        default=None,
        related_name="feature_designation")
    # new in v1.04
    location_class = models.ForeignKey(
        GeographicLocationClass,
        null=True,
        default=None)

    @property
    def point(self):
        if self.point_pos:
            coo = self.point_pos.split(' ')
            return Point(float(coo[0]), float(coo[1]))
        else:
            return Point(float(self.latitude), float(self.longitude))

    def __unicode__(self,):
        return "%s - %s" % (self.activity, self.name)


class Ffs(models.Model):
    activity = models.ForeignKey(Activity)
    extraction_date = models.DateField(null=True, default=None)
    priority = models.BooleanField(default=False)
    phaseout_year = models.IntegerField(max_length=4, null=True)

    def __unicode__(self,):
        return "%s" % (self.extraction_date)


class FfsForecast(models.Model):
    ffs = models.ForeignKey(Ffs)
    year = models.IntegerField(max_length=4, null=True)
    currency = models.ForeignKey(Currency)
    value_date = models.DateField(null=True, default=None)
    value = models.DecimalField(max_digits=15, decimal_places=2)

    def __unicode__(self,):
        return "%s" % (self.year)


class CrsAdd(models.Model):
    activity = models.ForeignKey(Activity)
    aid_type_flag = models.ForeignKey(AidTypeFlag)
    aid_type_flag_significance = models.IntegerField(null=True, default=None)

    def __unicode__(self,):
        return "%s" % (self.id)


class CrsAddLoanTerms(models.Model):
    crs_add = models.ForeignKey(CrsAdd)
    rate_1 = models.IntegerField(null=True, default=None)
    rate_2 = models.IntegerField(null=True, default=None)
    repayment_type = models.ForeignKey(
        LoanRepaymentType,
        null=True,
        default=None)
    repayment_plan = models.ForeignKey(
        LoanRepaymentPeriod,
        null=True,
        default=None)
    repayment_plan_text = models.TextField(null=True, default=None)
    commitment_date = models.DateField(null=True, default=None)
    repayment_first_date = models.DateField(null=True, default=None)
    repayment_final_date = models.DateField(null=True, default=None)

    def __unicode__(self,):
        return "%s" % (self.crs_add_id)


class CrsAddLoanStatus(models.Model):
    crs_add = models.ForeignKey(CrsAdd)
    year = models.IntegerField(null=True, default=None)
    value_date = models.DateField(null=True, default=None)
    currency = models.ForeignKey(Currency, null=True, default=None)
    interest_received = models.DecimalField(
        null=True,
        default=None,
        max_digits=15,
        decimal_places=2)
    principal_outstanding = models.DecimalField(
        null=True,
        default=None,
        max_digits=15,
        decimal_places=2)
    principal_arrears = models.DecimalField(
        null=True,
        default=None,
        max_digits=15,
        decimal_places=2)
    interest_arrears = models.DecimalField(
        null=True,
        default=None,
        max_digits=15,
        decimal_places=2)

    def __unicode__(self):
        return "%s" % (self.year)
