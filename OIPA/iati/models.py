from geodata.models import Country, Region
from activity_manager import ActivityManager
from location_manager import LocationManager
from document_manager import DocumentManager
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
from iati_vocabulary.models import HumanitarianScopeVocabulary
from iati_vocabulary.models import IndicatorVocabulary
from iati_organisation.models import Organisation

from djorm_pgfulltext.models import SearchManager
from djorm_pgfulltext.fields import VectorField
from decimal import Decimal
from iati_synchroniser.models import Dataset

from iati_synchroniser.models import Publisher

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

    iati_identifier = models.CharField(max_length=150, blank=False, unique=True, db_index=True)
    # normalized for use in the API
    normalized_iati_identifier = models.CharField(max_length=150, blank=False, db_index=True)

    iati_standard_version = models.ForeignKey(Version)
    dataset = models.ForeignKey(Dataset, null=True, default=None)
    publisher = models.ForeignKey(Publisher, null=True, default=None)

    default_currency = models.ForeignKey(Currency, null=True, blank=True, default=None, related_name="default_currency")
    hierarchy = models.SmallIntegerField(choices=hierarchy_choices, default=1, blank=True, db_index=True)
    last_updated_model = models.DateTimeField(null=True, blank=True, auto_now=True)

    last_updated_datetime = models.DateTimeField(blank=True, null=True)

    # default_lang = models.CharField(max_length=2, blank=True, null=True)
    default_lang = models.ForeignKey(Language, null=True, blank=True, default=None)
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
    humanitarian = models.NullBooleanField(null=True, blank=True)

    # this is reported on activity/reporting-org
    secondary_reporter = models.BooleanField(default=False)

    # added data
    is_searchable = models.BooleanField(default=True, db_index=True)

    # is this valid IATI?
    # this value should be updated on every O2M, M2M save and activity update
    # is_valid_iati = models.BooleanField(default=False, db_index=True)

    # is this activity published to the IATI registry?
    published = models.BooleanField(default=False, db_index=True)
    # is this activity marked as being published in the next export?
    ready_to_publish = models.BooleanField(default=False, db_index=True)
    # is this activity changed from the originally parsed version?
    modified = models.BooleanField(default=False, db_index=True)



    objects = ActivityManager(
        ft_model = ActivitySearch, # model that contains the ft indexes
        fields = ('title', 'description'), # fields on the model 
        config = 'pg_catalog.simple', # default dictionary to use
        search_field = 'text', # text field for all search fields,
        auto_update_search_field = False, # TODO: make this compatible with M2M - 2016-01-11
    )



    def __unicode__(self):
        return self.iati_identifier

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

    def get_activity(self):
        return self

    def is_valid_iati(self):
        """
        Check if all required foreign objects are created
        """
        # TODO: create this method - 2016-10-03
        return True

    @property
    def get_providing_activities(self):
        providing_activities = []

        for transaction in self.transaction_set.all():
            if transaction.provider_organisation and transaction.provider_organisation.provider_activity:
                providing_activities.append(transaction.provider_organisation.provider_activity.id)

        return Activity.objects.filter(id__in=providing_activities).exclude(id=self.id).distinct()

    @property
    def get_provided_activities(self):
        return Activity.objects.filter(transaction__provider_organisation__provider_activity=self.id).exclude(id=self.id).distinct()


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

    def get_activity(self):
        return self.activity

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

    def get_activity(self):
        return self.activity



class ActivityParticipatingOrganisation(models.Model):
    ref = models.CharField(max_length=250, null=True, blank=True, default="")
    normalized_ref = models.CharField(blank=True, max_length=120, null=True, default=None, db_index=True)

    activity = models.ForeignKey(
        Activity,
        related_name="participating_organisations")

    # if in organisation standard
    organisation = models.ForeignKey(Organisation, null=True, blank=True, default=None, on_delete=models.SET_NULL)

    type = models.ForeignKey(OrganisationType, null=True, blank=True, default=None)
    role = models.ForeignKey(OrganisationRole, null=True, blank=True, default=None)

    # when organisation is not mentioned in transactions
    org_activity_id = models.CharField(max_length=150, blank=False, null=True, db_index=True)

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

    def get_activity(self):
        return self.activity



class ActivityPolicyMarker(models.Model):
    activity = models.ForeignKey(Activity)
    code = models.ForeignKey(PolicyMarker)
    vocabulary = models.ForeignKey(PolicyMarkerVocabulary)
    vocabulary_uri = models.URLField(null=True, blank=True)
    significance = models.ForeignKey(
        PolicySignificance,
        null=True,
        blank=True,
        )
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    def __unicode__(self,):
        return "code: %s - significance: %s" % (self.code, self.significance.code)

    class Meta:
        verbose_name = 'Policy marker'
        verbose_name_plural = 'Policy markers'

    def get_activity(self):
        return self.activity


class ActivitySector(models.Model):
    activity = models.ForeignKey(Activity)
    sector = models.ForeignKey(Sector, null=True, blank=True, default=None)
    vocabulary = models.ForeignKey(SectorVocabulary, null=True, blank=True, default=None)
    vocabulary_uri = models.URLField(null=True, blank=True)
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

    def get_activity(self):
        return self.activity



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

    def get_activity(self):
        return self.activity



class CountryBudgetItem(models.Model):
    activity = models.OneToOneField(Activity, related_name="country_budget_items")
    vocabulary = models.ForeignKey(BudgetIdentifierVocabulary)

    def get_activity(self):
        return self.activity


class HumanitarianScope(models.Model):
    activity = models.ForeignKey(Activity)
    code = models.CharField(max_length=100)
    vocabulary = models.ForeignKey(HumanitarianScopeVocabulary)
    vocabulary_uri = models.URLField(null=True, blank=True)
    type = models.ForeignKey(HumanitarianScopeType)

    def get_activity(self):
        return self.activity


class BudgetItem(models.Model):
    country_budget_item = models.ForeignKey(CountryBudgetItem)
    code = models.ForeignKey(BudgetIdentifier)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=None)

    def get_activity(self):
        return self.country_budget_item.activity



class BudgetItemDescription(models.Model):
    budget_item = models.OneToOneField(BudgetItem, related_name="description")
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')


    def get_activity(self):
        return self.budget_item.country_budget_item.activity


class ActivityRecipientRegion(models.Model):
    activity = models.ForeignKey(Activity)
    region = models.ForeignKey(Region)
    vocabulary = models.ForeignKey(RegionVocabulary, default=1)
    vocabulary_uri = models.URLField(null=True, blank=True)
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

    def get_activity(self):
        return self.activity


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

    def get_activity(self):
        return self.activity


class ActivityWebsite(models.Model):
    activity = models.ForeignKey(Activity)
    url = models.URLField()

    def __unicode__(self,):
        return "%s" % self.url

    def get_activity(self):
        return self.activity


class ContactInfo(models.Model):
    activity = models.ForeignKey(Activity)
    type = models.ForeignKey(ContactType, null=True, blank=True)
    telephone = models.CharField(max_length=100, default="", null=True, blank=True)
    email = models.TextField(default="", null=True, blank=True)
    website = models.CharField(max_length=255, default="", null=True, blank=True)
   
    def __unicode__(self,):
        return "type: %s" % self.type

    def get_activity(self):
        return self.activity


class ContactInfoOrganisation(models.Model):
    contact_info = models.OneToOneField(ContactInfo, related_name="organisation", default=None)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')


class ContactInfoDepartment(models.Model):
    contact_info = models.OneToOneField(ContactInfo, related_name="department", default=None)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    def get_activity(self):
        return self.contact_info.activity


class ContactInfoPersonName(models.Model):
    contact_info = models.OneToOneField(ContactInfo, related_name="person_name", default=None)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    def get_activity(self):
        return self.contact_info.activity



class ContactInfoJobTitle(models.Model):
    contact_info = models.OneToOneField(ContactInfo, related_name="job_title", default=None)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    def get_activity(self):
        return self.contact_info.activity



class ContactInfoMailingAddress(models.Model):
    contact_info = models.OneToOneField(ContactInfo, related_name="mailing_address", default=None)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    def get_activity(self):
        return self.contact_info.activity



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

    def get_activity(self):
        return self.current_activity


class DocumentLink(models.Model):
    activity = models.ForeignKey(Activity)
    url = models.TextField(max_length=500)
    file_format = models.ForeignKey(FileFormat, null=True, blank=True, default=None)
    categories = models.ManyToManyField(
        DocumentCategory,
        through="DocumentLinkCategory")

    iso_date = models.DateField(null=True, blank=True)

    def __unicode__(self,):
        return "url: %s" % self.url

    def get_activity(self):
        return self.activity

# enables saving before parent object is saved (workaround)
# TODO: eliminate the need for this
class DocumentLinkCategory(models.Model):
    document_link = models.ForeignKey(DocumentLink)
    category = models.ForeignKey(DocumentCategory)

    class Meta:
        verbose_name_plural = "Document link categories"

    def get_activity(self):
        return self.document_link.activity

class DocumentLinkLanguage(models.Model):
    document_link = models.ForeignKey(DocumentLink)
    language = models.ForeignKey(Language, null=True, blank=True, default=None)

    def get_activity(self):
        return self.document_link.activity

class DocumentLinkTitle(models.Model):
    document_link = models.OneToOneField(DocumentLink)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    def get_activity(self):
        return self.document_link.activity


class DocumentSearch(models.Model):
    document = models.OneToOneField('Document')
    content = VectorField()
    text = VectorField()
    last_reindexed = models.DateTimeField()

class Document(models.Model):
    document_link = models.OneToOneField(DocumentLink)
    long_url = models.TextField(max_length=500, default='')
    url_is_valid = models.BooleanField(default=False)
    document_name = models.CharField(max_length=500, default='')
    is_downloaded = models.BooleanField(default=False)
    document_content = models.TextField(default='')
    long_url_hash = models.CharField(max_length=500, default='')
    file_hash = models.CharField(max_length=500, default='')
    document_or_long_url_changed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=True)

    objects = DocumentManager(
        ft_model = DocumentSearch, # model that contains the ft indexes
        fields = ('content'), # fields on the model 
        config = 'pg_catalog.simple', # default dictionary to use
        search_field = 'text', # text field for all search fields,
        auto_update_search_field = False, # TODO: make this compatible with M2M - 2016-01-11
    )

    def __unicode__(self):
        return self.id

    class Meta:
        ordering = ['id']
        verbose_name_plural = "documents"

        index_together = [
            ["created_at", "id"],
        ]

    def get_activity(self):
        return self.document_link.activity

class Result(models.Model):
    activity = models.ForeignKey(Activity)
    type = models.ForeignKey(ResultType, null=True, blank=True, default=None)
    aggregation_status = models.BooleanField(default=False)

    def __unicode__(self,):
        return "Result"

    def get_activity(self):
        return self.activity


class ResultTitle(models.Model):
    result = models.OneToOneField(Result)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    def get_activity(self):
        return self.result.activity


class ResultDescription(models.Model):
    result = models.OneToOneField(Result)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    def get_activity(self):
        return self.result.activity


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

    def get_activity(self):
        return self.result.activity

    def __unicode__(self,):
        return "baseline year: %s" % self.baseline_year

class ResultIndicatorReference(models.Model):
    result_indicator = models.ForeignKey(ResultIndicator)
    code = models.CharField(max_length=255)
    vocabulary = models.ForeignKey(IndicatorVocabulary)
    # TODO: this should be renamed to vocabulary_uri in IATI standard... - 2016-06-03
    indicator_uri = models.URLField(null=True, blank=True)

    def get_activity(self):
        return self.result_indicator.result.activity


class ResultIndicatorTitle(models.Model):
    result_indicator = models.OneToOneField(ResultIndicator)
    primary_name = models.CharField(
        max_length=255,
        null=False,
        blank=True,
        default="",
        db_index=True)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    def get_activity(self):
        return self.result_indicator.result.activity



class ResultIndicatorDescription(models.Model):
    result_indicator = models.OneToOneField(ResultIndicator)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    def get_activity(self):
        return self.result_indicator.result.activity



class ResultIndicatorBaselineComment(models.Model):
    result_indicator = models.OneToOneField(ResultIndicator)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    def get_activity(self):
        return self.result_indicator.result.activity



class ResultIndicatorPeriod(models.Model):
    result_indicator = models.ForeignKey(ResultIndicator)
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)

    target = models.DecimalField(max_digits=25, decimal_places=10, null=True, blank=True)
    actual = models.DecimalField(max_digits=25, decimal_places=10, null=True, blank=True)

    def __unicode__(self,):
        return "target: %s, actual: %s" % (self.target, self.actual)

    def get_activity(self):
        return self.result_indicator.result.activity


class ResultIndicatorPeriodTargetLocation(models.Model):
    result_indicator_period = models.ForeignKey(ResultIndicatorPeriod)
    ref = models.CharField(max_length=50)
    location = models.ForeignKey('Location')

    def __unicode__(self,):
        return "%s" % self.ref

    def get_activity(self):
        return self.result_indicator_period.result_indicator.result.activity


class ResultIndicatorPeriodActualLocation(models.Model):
    result_indicator_period = models.ForeignKey(ResultIndicatorPeriod)
    ref = models.CharField(max_length=50)
    location = models.ForeignKey('Location')

    def __unicode__(self,):
        return "%s" % self.ref

    def get_activity(self):
        return self.result_indicator_period.result_indicator.result.activity



class ResultIndicatorPeriodTargetDimension(models.Model):
    result_indicator_period = models.ForeignKey(ResultIndicatorPeriod)
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

    def __unicode__(self,):
        return "%s: %s" % (self.name, self.value)

    def get_activity(self):
        return self.result_indicator_period.result_indicator.result.activity


class ResultIndicatorPeriodActualDimension(models.Model):
    result_indicator_period = models.ForeignKey(ResultIndicatorPeriod)
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

    def __unicode__(self,):
        return "%s: %s" % (self.name, self.value)

    def get_activity(self):
        return self.result_indicator_period.result_indicator.result.activity


class ResultIndicatorPeriodTargetComment(models.Model):
    result_indicator_period = models.OneToOneField(ResultIndicatorPeriod)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    def get_activity(self):
        return self.result_indicator_period.result_indicator.result.activity



class ResultIndicatorPeriodActualComment(models.Model):
    result_indicator_period = models.OneToOneField(ResultIndicatorPeriod)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    def get_activity(self):
        return self.result_indicator_period.result_indicator.result.activity



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

    def get_activity(self):
        return self.activity



class Budget(models.Model):
    activity = models.ForeignKey(Activity)
    type = models.ForeignKey(BudgetType, null=True, blank=True, default=None)
    status = models.ForeignKey(BudgetStatus, default=1)
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

    def get_activity(self):
        return self.activity




# same as TransactionSector, to set percentages per budget item per sector
# this makes calculations easier (no subqueries required).
class BudgetSector(models.Model):
    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE)
    
    sector = models.ForeignKey(
        Sector,
        on_delete=models.CASCADE)

    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2)

    def __unicode__(self, ):
        return "%s - %s" % (self.budget.id, self.sector.code)

    def get_activity(self):
        return self.budget.activity




class PlannedDisbursement(models.Model):

    activity = models.ForeignKey(Activity)
    type = models.ForeignKey(BudgetType, null=True, blank=True, default=None)
    period_start = models.DateField(blank=True, default=None)
    period_end = models.DateField(null=True, blank=True, default=None)
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

    def get_activity(self):
        return self.activity


    # budget_type = models.ForeignKey(BudgetType, null=True, blank=True, default=None)
    # activity = models.ForeignKey(Activity)
    # period_start = models.CharField(max_length=100, default="")
    # period_end = models.CharField(max_length=100, default="")
    # value_date = models.DateField(null=True, blank=True)
    # value = models.DecimalField(max_digits=15, decimal_places=2)
    # xdr_value = models.DecimalField(max_digits=20, decimal_places=7, default=0)
    # value_string = models.CharField(max_length=50)
    # currency = models.ForeignKey(Currency, null=True, blank=True, default=None)
    # # updated = models.DateField(null=True, default=None) deprecated

    # def __unicode__(self,):
    #     return "value: %s - period_start: %s - period_end: %s" % (self.value, self.period_start, self.period_end)

class PlannedDisbursementProvider(models.Model):
    ref = models.CharField(blank=True, default="", max_length=250)
    normalized_ref = models.CharField(max_length=120, default="")

    organisation = models.ForeignKey(
        Organisation,
        related_name="planned_disbursement_providing_organisation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None)
    
    type = models.ForeignKey(
        OrganisationType, 
        null=True, 
        default=None, 
        blank=True
    )

    provider_activity = models.ForeignKey(
        Activity,
        related_name="planned_disbursement_provider_activity",
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

    planned_disbursement = models.OneToOneField(
        PlannedDisbursement,
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


    def get_activity(self):
        return self.planned_disbursement.activity


class PlannedDisbursementReceiver(models.Model):
    ref = models.CharField(blank=True, default="", max_length=250)
    normalized_ref = models.CharField(max_length=120, default="")

    organisation = models.ForeignKey(
        Organisation,
        related_name="planned_disbursement_receiving_organisation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None)
    type = models.ForeignKey(
        OrganisationType, 
        null=True, 
        default=None, 
        blank=True
    )

    receiver_activity = models.ForeignKey(
        Activity,
        related_name="planned_disbursement_receiver_activity",
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

    planned_disbursement = models.OneToOneField(
        PlannedDisbursement,
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

    def get_activity(self):
        return self.planned_disbursement.activity

class Conditions(models.Model):
    activity = models.OneToOneField(Activity, related_name="conditions")
    attached = models.BooleanField()

    # def __unicode__(self,):
    #     return "text: %s - type: %s" % (self.text[:30], self.type)

    def get_activity(self):
        return self.activity

class Condition(models.Model):
    conditions = models.ForeignKey(Conditions)
    type = models.ForeignKey(ConditionType, null=True, blank=True, default=None)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    # def __unicode__(self,):
    #     return "text: %s - type: %s" % (self.text[:30], self.type)

    def get_activity(self):
        return self.conditions.activity


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
    point_pos = PointField(
        null=True, 
        blank=False,
        default=None,
        spatial_index=True,
        srid=4326,
        geography=True)
    exactness = models.ForeignKey(GeographicExactness, null=True, blank=True, default=None)

    objects = LocationManager()

    def __unicode__(self,):
        return "Location: %s" % self.point_pos

    def get_activity(self):
        return self.activity


# TODO: move to codelist
class LocationAdministrative(models.Model):
    location = models.ForeignKey(Location)
    code = models.CharField(max_length=255)
    vocabulary = models.ForeignKey(
        GeographicVocabulary,
        related_name="administrative_vocabulary")
    level = models.IntegerField(null=True, blank=True, default=None)

    def get_activity(self):
        return self.location.activity

class LocationName(models.Model):
    location = models.OneToOneField(Location, related_name="name")
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    def get_activity(self):
        return self.location.activity


class LocationDescription(models.Model):
    location = models.OneToOneField(Location, related_name="description")
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    def get_activity(self):
        return self.location.activity


class LocationActivityDescription(models.Model):
    location = models.OneToOneField(Location, related_name="activity_description")
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    def get_activity(self):
        return self.location.activity


class Fss(models.Model):
    activity = models.ForeignKey(Activity)
    extraction_date = models.DateField()
    priority = models.BooleanField(default=False)
    phaseout_year = models.IntegerField(null=True, blank=True)

    def __unicode__(self,):
        return "%s" % self.extraction_date

    def get_activity(self):
        return self.activity


class FssForecast(models.Model):
    fss = models.ForeignKey(Fss)
    year = models.IntegerField()
    currency = models.ForeignKey(Currency)
    value_date = models.DateField()
    value = models.DecimalField(max_digits=15, decimal_places=2)

    def __unicode__(self,):
        return "%s" % self.year

    def get_activity(self):
        return self.fss.activity


class CrsAdd(models.Model):
    activity = models.ForeignKey(Activity)
    channel_code = models.CharField(max_length=50, null=True, blank=True)

    def __unicode__(self,):
        return "%s" % self.id

    def get_activity(self):
        return self.activity


class CrsAddOtherFlags(models.Model):
    crs_add = models.ForeignKey(CrsAdd, related_name="other_flags")
    other_flags = models.ForeignKey(OtherFlags)
    significance = models.BooleanField()

    def __unicode__(self,):
        return "%s" % self.id

    def get_activity(self):
        return self.crs_add.activity


class CrsAddLoanTerms(models.Model):
    crs_add = models.OneToOneField(CrsAdd, related_name="loan_terms")
    rate_1 = models.DecimalField(
        null=True,
        blank=True,
        default=None,
        max_digits=5,
        decimal_places=2)
    rate_2 = models.DecimalField(
        null=True,
        blank=True,
        default=None,
        max_digits=5,
        decimal_places=2)
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

    def get_activity(self):
        return self.crs_add.activity


class CrsAddLoanStatus(models.Model):
    crs_add = models.OneToOneField(CrsAdd, related_name="loan_status")
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

    def get_activity(self):
        return self.crs_add.activity


class ActivityDate(models.Model):
    activity = models.ForeignKey(Activity)
    iso_date = models.DateField()
    type = models.ForeignKey(ActivityDateType)

    def __unicode__(self):
        return "type: %s - iso_date: %s" % (self.type, self.iso_date.strftime('%Y-%m-%d'))

    def get_activity(self):
        return self.activity


class LegacyData(models.Model):
    activity = models.ForeignKey(Activity)
    name = models.CharField(max_length=150, null=True, blank=True)
    value = models.CharField(max_length=200, null=True, blank=True)
    iati_equivalent = models.CharField(max_length=150, null=True, blank=True)

    def __unicode__(self):
        return "%s" % self.name

    def get_activity(self):
        return self.activity

