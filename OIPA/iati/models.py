from geodata.models import Country, Region
from activity_manager import ActivityManager
from django.contrib.gis.db.models import PointField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from iati_codelists.models import *
from iati_vocabulary.models import RegionVocabulary
from iati_vocabulary.models import GeographicVocabulary
from iati_vocabulary.models import PolicyMarkerVocabulary
from iati_vocabulary.models import SectorVocabulary
from iati_vocabulary.models import BudgetIdentifierVocabulary
from iati_organisation.models import Organisation

from djorm_pgfulltext.fields import VectorField
from decimal import Decimal


# TODO: separate this
class Narrative(models.Model):
    # references an actual related model which has a corresponding narrative
    related_content_type = models.ForeignKey(ContentType, related_name='related_agent')
    related_object_id = models.IntegerField(
        verbose_name='related object',
        null=True,
        db_index=True)
    related_object = GenericForeignKey('related_content_type', 'related_object_id')

    activity = models.ForeignKey('Activity')

    language = models.ForeignKey(Language)
    content = models.TextField()

    def __unicode__(self,):
        return "%s" % self.content[:30]

    class Meta:
        index_together = [('related_content_type', 'related_object_id')]


class ActivitySearch(models.Model):
    activity = models.OneToOneField('Activity')
    iati_identifier = VectorField()
    text = VectorField()
    title = VectorField()
    description = VectorField()
    reporting_org = VectorField()
    participating_org = VectorField()
    recipient_country = VectorField()
    recipient_region = VectorField()
    sector = VectorField()
    document_link = VectorField()
    last_reindexed = models.DateTimeField()


class Activity(models.Model):
    hierarchy_choices = (
        (1, u"Parent"),
        (2, u"Child"),
    )

    id = models.CharField(max_length=150, primary_key=True, blank=False)
    iati_identifier = models.CharField(max_length=150, blank=False, db_index=True)

    iati_standard_version = models.ForeignKey(Version)
    xml_source_ref = models.CharField(max_length=200, default="", db_index=True)

    default_currency = models.ForeignKey(Currency, null=True, blank=True, default=None, related_name="default_currency")
    hierarchy = models.SmallIntegerField(choices=hierarchy_choices, default=1, blank=True, db_index=True)
    last_updated_model = models.DateTimeField(null=True, blank=True, auto_now=True)

    last_updated_datetime = models.DateTimeField(blank=True, null=True)

    default_lang = models.CharField(max_length=2, blank=True, null=True)
    linked_data_uri = models.CharField(max_length=100, blank=True, null=True, default="")

    planned_start = models.DateField(null=True, blank=True, default=None, db_index=True)
    actual_start = models.DateField(null=True, blank=True, default=None, db_index=True)
    start_date = models.DateField(null=True, blank=True, default=None, db_index=True)
    planned_end = models.DateField(null=True, blank=True, default=None, db_index=True)
    actual_end = models.DateField(null=True, blank=True, default=None, db_index=True)
    end_date = models.DateField(null=True, blank=True, default=None, db_index=True)

    activity_status = models.ForeignKey(
        ActivityStatus,
        null=True,
        blank=True,
        default=None)

    policy_marker = models.ManyToManyField(
        PolicyMarker,
        through="ActivityPolicyMarker")
    sector = models.ManyToManyField(
        Sector,
        through="ActivitySector")
    recipient_country = models.ManyToManyField(
        Country,
        through="ActivityRecipientCountry")
    recipient_region = models.ManyToManyField(
        Region,
        through="ActivityRecipientRegion")

    collaboration_type = models.ForeignKey(
        CollaborationType,
        null=True,
        blank=True,
        default=None)
    default_flow_type = models.ForeignKey(FlowType, null=True, blank=True, default=None)
    default_aid_type = models.ForeignKey(AidType, null=True, blank=True, default=None)
    default_finance_type = models.ForeignKey(FinanceType, null=True, blank=True, default=None)
    default_tied_status = models.ForeignKey(TiedStatus, null=True, blank=True, default=None)
    scope = models.ForeignKey(ActivityScope, null=True, blank=True, default=None)

    # @percentage on capital-spend
    capital_spend = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        default=None)
    # @attached on iati-conditions
    has_conditions = models.BooleanField(default=False)

    # added data
    is_searchable = models.BooleanField(default=True, db_index=True)

    objects = ActivityManager(
        ft_model = ActivitySearch, # model that contains the ft indexes
        fields = ('title', 'description'), # fields on the model 
        config = 'pg_catalog.simple', # default dictionary to use
        search_field = 'text', # text field for all search fields,
        auto_update_search_field = False, # TODO: make this compatible with M2M - 2016-01-11
    )

    def __unicode__(self):
        return self.id

    class Meta:
        ordering = ['id']
        verbose_name_plural = "activities"

        index_together = [
            ["planned_start", "id"],
            ["actual_start", "id"],
            ["start_date", "id"],
            ["planned_end", "id"],
            ["actual_end", "id"],
            ["end_date", "id"],
        ]


class AbstractActivityAggregation(models.Model):
    budget_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        db_index=True,
    )
    budget_currency = models.CharField(
        max_length=3,
        null=True, 
        default=None, 
        blank=True,
    )
    disbursement_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True, 
        db_index=True,
    )
    disbursement_currency = models.CharField(
        max_length=3,
        null=True,
        default=None,
        blank=True,
    )
    incoming_funds_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        db_index=True,
    )
    incoming_funds_currency = models.CharField(
        max_length=3,
        null=True,
        default=None,
        blank=True,
    )
    commitment_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        db_index=True,
    )
    commitment_currency = models.CharField(
        max_length=3,
        null=True,
        default=None,
        blank=True,
    )
    expenditure_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        db_index=True,
    )
    expenditure_currency = models.CharField(
        max_length=3,
        null=True,
        default=None,
        blank=True,
    )

    class Meta:
        abstract = True

        index_together = [
            ["budget_value", "activity"],
            ["disbursement_value", "activity"],
            ["incoming_funds_value", "activity"],
            ["commitment_value", "activity"],
            ["expenditure_value", "activity"],
        ]


class ActivityAggregation(AbstractActivityAggregation):
    activity = models.OneToOneField(Activity, related_name="activity_aggregation", default=None)


class ChildAggregation(AbstractActivityAggregation):
    activity = models.OneToOneField(Activity, related_name="child_aggregation", default=None)


class ActivityPlusChildAggregation(AbstractActivityAggregation):
    activity = models.OneToOneField(Activity, related_name="activity_plus_child_aggregation", default=None)


class Title(models.Model):
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    # related name allows title to be accessed from activity.title
    activity = models.OneToOneField(Activity, related_name="title")

    def __unicode__(self,):
        return "Title"


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


class ActivityReportingOrganisation(models.Model):
    ref = models.CharField(max_length=250, db_index=True)
    normalized_ref = models.CharField(max_length=120, db_index=True, default="", blank=True)

    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    activity = models.ForeignKey(
        Activity,
        related_name="reporting_organisations")

    # if in organisation standard
    organisation = models.ForeignKey(Organisation, null=True, default=None, on_delete=models.SET_NULL)
    type = models.ForeignKey(OrganisationType, null=True, default=None, blank=True)

    secondary_reporter = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Reporting organisation'
        verbose_name_plural = 'Reporting organisations'

    def __unicode__(self,):
        return "ref: %s" % self.ref

class ActivityParticipatingOrganisation(models.Model):
    ref = models.CharField(max_length=250, null=True, blank=True, default="")
    normalized_ref = models.CharField(blank=True, max_length=120, null=True, default=None, db_index=True)

    activity = models.ForeignKey(
        Activity,
        related_name="participating_organisations")

    # if in organisation standard
    organisation = models.ForeignKey(Organisation, null=True, blank=True, default=None)

    type = models.ForeignKey(OrganisationType, null=True, blank=True, default=None)
    role = models.ForeignKey(OrganisationRole, null=True, blank=True, default=None)

    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')
    
    # TODO: Workaround for IATI ref limitation - 2015-11-26
    primary_name = models.TextField(blank=True)

    def __unicode__(self,):
        return "name: %s - role: %s" % (self.primary_name, self.role)

    class Meta:
        verbose_name = 'Participating organisation'
        verbose_name_plural = 'Participating organisations'


class ActivityPolicyMarker(models.Model):
    activity = models.ForeignKey(Activity)
    code = models.ForeignKey(PolicyMarker)
    vocabulary = models.ForeignKey(PolicyMarkerVocabulary)
    significance = models.ForeignKey(
        PolicySignificance)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    def __unicode__(self,):
        return "code: %s - significance: %s" % (self.code, self.significance.code)

    class Meta:
        verbose_name = 'Policy marker'
        verbose_name_plural = 'Policy markers'


class ActivitySector(models.Model):
    activity = models.ForeignKey(Activity)
    sector = models.ForeignKey(Sector, null=True, blank=True, default=None)
    vocabulary = models.ForeignKey(SectorVocabulary, null=True, blank=True, default=None)
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        default=None)

    def __unicode__(self,):
        return "name: %s" % self.sector

    class Meta:
        verbose_name = 'Sector'
        verbose_name_plural = 'Sectors'


class ActivityRecipientCountry(models.Model):
    activity = models.ForeignKey(Activity)
    country = models.ForeignKey(Country)
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        default=None)

    def __unicode__(self,):
        return "name: %s" % self.country.name

    class Meta:
        verbose_name = 'Recipient country'
        verbose_name_plural = 'Recipient countries'


class CountryBudgetItem(models.Model):
    activity = models.ForeignKey(Activity)
    vocabulary = models.ForeignKey(BudgetIdentifierVocabulary)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=None)


class BudgetItem(models.Model):
    country_budget_item = models.ForeignKey(CountryBudgetItem)
    code = models.ForeignKey(BudgetIdentifier)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=None)


class BudgetItemDescription(models.Model):
    budget_item = models.ForeignKey(BudgetItem)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')


class ActivityRecipientRegion(models.Model):
    activity = models.ForeignKey(Activity)
    region = models.ForeignKey(Region)
    vocabulary = models.ForeignKey(RegionVocabulary, default=1)
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        default=None)

    def __unicode__(self,):
        return "name: %s" % self.region

    class Meta:
        verbose_name = 'Recipient region'
        verbose_name_plural = 'Recipient regions'


class OtherIdentifier(models.Model):
    activity = models.ForeignKey(Activity)
    identifier = models.CharField(max_length=100)
    owner_ref = models.CharField(max_length=100, default="")
    # owner_name = models.CharField(max_length=100, default="")
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')
    type = models.ForeignKey(OtherIdentifierType, null=True, blank=True)

    def __unicode__(self,):
        return "identifier: %s" % self.identifier


class ActivityWebsite(models.Model):
    activity = models.ForeignKey(Activity)
    url = models.URLField()

    def __unicode__(self,):
        return "%s" % self.url


#   Class not truly correct, attributes fully open
class ContactInfo(models.Model):
    activity = models.ForeignKey(Activity)
    type = models.ForeignKey(ContactType, null=True, blank=True)
    # person_name = GenericRelation(Narrative, related_query_name="person_name")
    # organisation = GenericRelation(ContactInfoOrganisationNarrative)
    # person_name = models.CharField(max_length=100, default="", null=True, blank=True)
    # organisation = models.CharField(max_length=100, default="", null=True, blank=True)
    telephone = models.CharField(max_length=100, default="", null=True, blank=True)
    email = models.TextField(default="", null=True, blank=True)
    mailing_address = models.TextField(default="", null=True, blank=True)
    website = models.CharField(max_length=255, default="", null=True, blank=True)
    job_title = models.CharField(max_length=150, default="", null=True, blank=True)

    def __unicode__(self,):
        return "type: %s" % self.type

# class ContactInfoOrganisationNarrative(Narrative):
#     pass
# TODO: inherit narratives and link from contactinfo? (API inconsistency?)


class ContactInfoOrganisation(models.Model):
    contact_info = models.ForeignKey(ContactInfo)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')


class ContactInfoDepartment(models.Model):
    contact_info = models.ForeignKey(ContactInfo)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')


class ContactInfoPersonName(models.Model):
    contact_info = models.ForeignKey(ContactInfo)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')


class ContactInfoJobTitle(models.Model):
    contact_info = models.ForeignKey(ContactInfo)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')


class ContactInfoMailingAddress(models.Model):
    contact_info = models.ForeignKey(ContactInfo)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')


class ContactInfoTelephone(models.Model):
    contact_info = models.ForeignKey(ContactInfo)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

# class transaction_description(models.Model):
#     transaction = models.ForeignKey(transaction)
#     type = models.ForeignKey(description_type, null=True, default=None)
#     language = models.ForeignKey(language, null=True, default=None)
#     description = models.TextField(default="")
#
#     def __unicode__(self,):
#         return "%s - %s" % (self.code, self.name)


class PlannedDisbursement(models.Model):
    budget_type = models.ForeignKey(BudgetType, null=True, blank=True, default=None)
    activity = models.ForeignKey(Activity)
    period_start = models.CharField(max_length=100, default="")
    period_end = models.CharField(max_length=100, default="")
    value_date = models.DateField(null=True, blank=True)
    value = models.DecimalField(max_digits=15, decimal_places=2)
    xdr_value = models.DecimalField(max_digits=20, decimal_places=7, default=0)
    value_string = models.CharField(max_length=50)
    currency = models.ForeignKey(Currency, null=True, blank=True, default=None)
    # updated = models.DateField(null=True, default=None) deprecated

    def __unicode__(self,):
        return "value: %s - period_start: %s - period_end: %s" % (self.value, self.period_start, self.period_end)


class RelatedActivity(models.Model):
    current_activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE)
    ref_activity = models.ForeignKey(
        Activity,
        related_name="ref_activity",
        null=True,
        blank=True,
        on_delete=models.SET_NULL)
    type = models.ForeignKey(
        RelatedActivityType,
        max_length=200,
        null=True,
        blank=True,
        default=None)
    ref = models.CharField(db_index=True, max_length=200, default="", blank=True)

    def __unicode__(self,):
        return "ref-activity: %s" % self.ref_activity

    class Meta:
        verbose_name_plural = "related activities"


class DocumentLink(models.Model):
    activity = models.ForeignKey(Activity)
    url = models.TextField(max_length=500)
    file_format = models.ForeignKey(FileFormat, null=True, blank=True, default=None)
    categories = models.ManyToManyField(
        DocumentCategory,
        through="DocumentLinkCategory")

    def __unicode__(self,):
        return "url: %s" % self.url


# enables saving before parent object is saved (workaround)
# TODO: eliminate the need for this
class DocumentLinkCategory(models.Model):
    document_link = models.ForeignKey(DocumentLink)
    category = models.ForeignKey(DocumentCategory)

    class Meta:
        verbose_name_plural = "Document link categories"


class DocumentLinkLanguage(models.Model):
    document_link = models.ForeignKey(DocumentLink)
    language = models.ForeignKey(Language, null=True, blank=True, default=None)


# TODO: enforce one-to-one
class DocumentLinkTitle(models.Model):
    document_link = models.ForeignKey(DocumentLink)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')


class Result(models.Model):
    activity = models.ForeignKey(Activity)
    type = models.ForeignKey(ResultType, null=True, blank=True, default=None)
    aggregation_status = models.BooleanField(default=False)

    def __unicode__(self,):
        return "Result"


class ResultTitle(models.Model):
    result = models.OneToOneField(Result)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')


class ResultDescription(models.Model):
    result = models.OneToOneField(Result)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')


class ResultIndicator(models.Model):
    result = models.ForeignKey(Result)
    baseline_year = models.IntegerField(null=True, blank=True, default=None)
    baseline_value = models.CharField(null=True, blank=True, default=None, max_length=100)
    measure = models.ForeignKey(
        IndicatorMeasure,
        null=True,
        blank=True,
        default=None)
    ascending = models.BooleanField(default=True)

    def __unicode__(self,):
        return "baseline year: %s" % self.baseline_year


class ResultIndicatorTitle(models.Model):
    result_indicator = models.OneToOneField(ResultIndicator)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')


class ResultIndicatorDescription(models.Model):
    result_indicator = models.OneToOneField(ResultIndicator)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')


class ResultIndicatorBaselineComment(models.Model):
    result_indicator = models.OneToOneField(ResultIndicator)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')


class ResultIndicatorPeriod(models.Model):
    result_indicator = models.ForeignKey(ResultIndicator)
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)

    target = models.CharField(max_length=50, default="", blank=True)
    actual = models.CharField(max_length=50, default="", blank=True)

    def __unicode__(self,):
        return "%s" % self.result_indicator


class ResultIndicatorPeriodTargetComment(models.Model):
    result_indicator_period = models.OneToOneField(ResultIndicatorPeriod)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')


class ResultIndicatorPeriodActualComment(models.Model):
    result_indicator_period = models.OneToOneField(ResultIndicatorPeriod)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')


class Description(models.Model):
    activity = models.ForeignKey(Activity)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    # TODO: set a default or require
    type = models.ForeignKey(
        DescriptionType,
        related_name="description_type",
        null=True,
        blank=True,
        default=None)

    def __unicode__(self,):
        return "Description with type %s" % self.type


class Budget(models.Model):
    activity = models.ForeignKey(Activity)
    type = models.ForeignKey(BudgetType, null=True, blank=True, default=None)
    period_start = models.DateField(blank=True, default=None)
    period_end = models.DateField(blank=True, default=None)
    value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    value_string = models.CharField(max_length=50)
    value_date = models.DateField(null=True, blank=True, default=None)
    currency = models.ForeignKey(Currency, null=True, blank=True, default=None)

    xdr_value = models.DecimalField(max_digits=20, decimal_places=7, default=Decimal(0))
    usd_value = models.DecimalField(max_digits=20, decimal_places=7, default=Decimal(0))
    eur_value = models.DecimalField(max_digits=20, decimal_places=7, default=Decimal(0))
    gbp_value = models.DecimalField(max_digits=20, decimal_places=7, default=Decimal(0))
    jpy_value = models.DecimalField(max_digits=20, decimal_places=7, default=Decimal(0))
    cad_value = models.DecimalField(max_digits=20, decimal_places=7, default=Decimal(0))

    def __unicode__(self,):
        return "value: %s - period_start: %s - period_end: %s" % (str(self.value), self.period_start, self.period_end)


class Condition(models.Model):
    activity = models.ForeignKey(Activity)
    text = models.TextField(default="")
    type = models.ForeignKey(ConditionType, null=True, blank=True, default=None)

    def __unicode__(self,):
        return "text: %s - type: %s" % (self.text[:30], self.type)


class Location(models.Model):
    activity = models.ForeignKey(Activity)

    ref = models.CharField(max_length=200, default="", null=True, blank=True)
    location_reach = models.ForeignKey(
        GeographicLocationReach,
        null=True,
        blank=True,
        default=None,
        related_name="location_reach")

    # TODO: make location_id a one-to-one field?
    location_id_vocabulary = models.ForeignKey(
        GeographicVocabulary,
        null=True,
        blank=True,
        default=None,
        related_name="location_id_vocabulary")
    location_id_code = models.CharField(blank=True, max_length=255, default="")

    location_class = models.ForeignKey(
        GeographicLocationClass,
        null=True,
        blank=True,
        default=None)
    feature_designation = models.ForeignKey(
        LocationType,
        null=True,
        blank=True,
        default=None,
        related_name="feature_designation")

    point_srs_name = models.CharField(blank=True, max_length=255, default="")
    point_pos = PointField(null=True, blank=True)
    exactness = models.ForeignKey(GeographicExactness, null=True, blank=True, default=None)

    def __unicode__(self,):
        return "Location: %s" % self.point_pos


# TODO: move to codelist
class LocationAdministrative(models.Model):
    location = models.ForeignKey(Location)
    code = models.CharField(max_length=255)
    vocabulary = models.ForeignKey(
        GeographicVocabulary,
        related_name="administrative_vocabulary")
    level = models.IntegerField(null=True, blank=True, default=None)


class LocationName(models.Model):
    location = models.ForeignKey(Location)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')


class LocationDescription(models.Model):
    location = models.ForeignKey(Location)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')


class LocationActivityDescription(models.Model):
    location = models.ForeignKey(Location)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')


class Fss(models.Model):
    activity = models.ForeignKey(Activity)
    extraction_date = models.DateField(null=True, blank=True, default=None)
    priority = models.BooleanField(default=False)
    phaseout_year = models.IntegerField(null=True, blank=True)

    def __unicode__(self,):
        return "%s" % self.extraction_date


class FssForecast(models.Model):
    fss = models.ForeignKey(Fss)
    year = models.IntegerField(null=True, blank=True)
    currency = models.ForeignKey(Currency)
    value_date = models.DateField(null=True, blank=True, default=None)
    value = models.DecimalField(max_digits=15, decimal_places=2)

    def __unicode__(self,):
        return "%s" % self.year


class CrsAdd(models.Model):
    activity = models.ForeignKey(Activity)

    def __unicode__(self,):
        return "%s" % self.id


class CrsAddOtherFlags(models.Model):
    crs_add = models.ForeignKey(CrsAdd)
    other_flags = models.ForeignKey(OtherFlags)
    other_flags_significance = models.IntegerField(null=True, blank=True, default=None)

    def __unicode__(self,):
        return "%s" % self.id


class CrsAddLoanTerms(models.Model):
    crs_add = models.ForeignKey(CrsAdd)
    rate_1 = models.IntegerField(null=True, blank=True, default=None)
    rate_2 = models.IntegerField(null=True, blank=True, default=None)
    repayment_type = models.ForeignKey(
        LoanRepaymentType,
        null=True,
        blank=True,
        default=None)
    repayment_plan = models.ForeignKey(
        LoanRepaymentPeriod,
        null=True,
        blank=True,
        default=None)
    repayment_plan_text = models.TextField(null=True, blank=True, default="")
    commitment_date = models.DateField(null=True, blank=True, default=None)
    repayment_first_date = models.DateField(null=True, blank=True, default=None)
    repayment_final_date = models.DateField(null=True, blank=True, default=None)

    def __unicode__(self,):
        return "%s" % self.crs_add_id


class CrsAddLoanStatus(models.Model):
    crs_add = models.ForeignKey(CrsAdd)
    year = models.IntegerField(null=True, blank=True, default=None)
    value_date = models.DateField(null=True, blank=True, default=None)
    currency = models.ForeignKey(Currency, null=True, blank=True, default=None)
    interest_received = models.DecimalField(
        null=True,
        blank=True,
        default=None,
        max_digits=15,
        decimal_places=2)
    principal_outstanding = models.DecimalField(
        null=True,
        blank=True,
        default=None,
        max_digits=15,
        decimal_places=2)
    principal_arrears = models.DecimalField(
        null=True,
        blank=True,
        default=None,
        max_digits=15,
        decimal_places=2)
    interest_arrears = models.DecimalField(
        null=True,
        blank=True,
        default=None,
        max_digits=15,
        decimal_places=2)

    def __unicode__(self):
        return "%s" % self.year


class ActivityDate(models.Model):
    activity = models.ForeignKey(Activity)
    iso_date = models.DateField()
    type = models.ForeignKey(ActivityDateType)

    def __unicode__(self):
        return "type: %s - iso_date: %s" % (self.type, self.iso_date.strftime('%Y-%m-%d'))


class LegacyData(models.Model):
    activity = models.ForeignKey(Activity)
    name = models.CharField(max_length=150, null=True, blank=True)
    value = models.CharField(max_length=200, null=True, blank=True)
    iati_equivalent = models.CharField(max_length=150, null=True, blank=True)

    def __unicode__(self):
        return "%s" % self.name

