from decimal import Decimal

from django.contrib.contenttypes.fields import (
    GenericForeignKey, GenericRelation
)
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db.models import PointField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from djorm_pgfulltext.fields import VectorField

from geodata.models import Country, Region
from iati_codelists.models import (
    ActivityDateType, ActivityScope, ActivityStatus, AidType, BudgetIdentifier,
    BudgetStatus, BudgetType, CollaborationType, ConditionType, ContactType,
    CRSChannelCode, Currency, DescriptionType, DocumentCategory, FileFormat,
    FinanceType, FlowType, GeographicExactness, GeographicLocationClass,
    GeographicLocationReach, HumanitarianScopeType, IndicatorMeasure, Language,
    LoanRepaymentPeriod, LoanRepaymentType, LocationType, OrganisationRole,
    OrganisationType, OtherFlags, OtherIdentifierType, PolicyMarker,
    PolicySignificance, RelatedActivityType, ResultType, Sector, TiedStatus,
    Version
)
from iati_organisation.models import Organisation
from iati_synchroniser.models import Dataset, Publisher
from iati_vocabulary.models import (
    BudgetIdentifierVocabulary, GeographicVocabulary,
    HumanitarianScopeVocabulary, IndicatorVocabulary, PolicyMarkerVocabulary,
    RegionVocabulary, ResultVocabulary, SectorVocabulary, TagVocabulary
)

# FIXME: relative imports:!
from .activity_manager import ActivityManager
from .location_manager import LocationManager


class Narrative(models.Model):
    # references an actual related model which has a corresponding narrative
    related_content_type = models.ForeignKey(
        ContentType, related_name='related_agent', on_delete=models.CASCADE)
    related_object_id = models.IntegerField(
        verbose_name='related object',
        null=True,
        db_index=True)
    related_object = GenericForeignKey(
        'related_content_type', 'related_object_id')

    activity = models.ForeignKey('Activity', on_delete=models.CASCADE)

    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    content = models.TextField()

    def __unicode__(self,):
        return "%s" % self.content[:30]

    class Meta:
        index_together = [('related_content_type', 'related_object_id')]


class ActivitySearch(models.Model):
    activity = models.OneToOneField('Activity', on_delete=models.CASCADE)
    iati_identifier = models.CharField(max_length=255)
    title = models.TextField(null=True)
    description = models.TextField(null=True)
    reporting_org = models.TextField(null=True)
    participating_org = models.TextField(null=True)
    recipient_country = models.TextField(null=True)
    recipient_region = models.TextField(null=True)
    sector = models.TextField(null=True)
    document_link = models.TextField(null=True)
    last_reindexed = models.DateTimeField()

    search_vector_text = SearchVectorField(null=True)

    class Meta:
        indexes = [
            GinIndex(fields=['search_vector_text'])
        ]


class Activity(models.Model):
    hierarchy_choices = (
        (1, u"Parent"),
        (2, u"Child"),
    )

    iati_identifier = models.CharField(
        max_length=150, blank=False, unique=True, db_index=True)
    # normalized for use in the API
    normalized_iati_identifier = models.CharField(
        max_length=150, blank=False, db_index=True)

    iati_standard_version = models.ForeignKey(Version,
                                              on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, null=True, default=None,
                                on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, null=True, default=None,
                                  on_delete=models.CASCADE)

    default_currency = models.ForeignKey(
        Currency,
        null=True,
        blank=True,
        default=None,
        related_name="default_currency", on_delete=models.CASCADE)
    hierarchy = models.SmallIntegerField(
        choices=hierarchy_choices,
        default=1,
        blank=True,
        db_index=True)
    last_updated_model = models.DateTimeField(
        null=True, blank=True, auto_now=True)

    last_updated_datetime = models.DateTimeField(blank=True, null=True)

    default_lang = models.ForeignKey(Language, null=True, blank=True,
                                     default=None, on_delete=models.CASCADE)
    linked_data_uri = models.CharField(
        max_length=100, blank=True, null=True, default="")

    planned_start = models.DateField(
        null=True, blank=True, default=None, db_index=True)
    actual_start = models.DateField(
        null=True, blank=True, default=None, db_index=True)
    start_date = models.DateField(
        null=True, blank=True, default=None, db_index=True)
    planned_end = models.DateField(
        null=True, blank=True, default=None, db_index=True)
    actual_end = models.DateField(
        null=True, blank=True, default=None, db_index=True)
    end_date = models.DateField(
        null=True, blank=True, default=None, db_index=True)

    activity_status = models.ForeignKey(
        ActivityStatus,
        null=True,
        blank=True,
        default=None, on_delete=models.CASCADE)

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
        default=None, on_delete=models.CASCADE)
    default_flow_type = models.ForeignKey(
        FlowType, null=True, blank=True, default=None,
        on_delete=models.CASCADE)
    default_aid_type = models.ForeignKey(
        AidType, null=True, blank=True, default=None, on_delete=models.CASCADE)
    default_finance_type = models.ForeignKey(
        FinanceType, null=True, blank=True,
        default=None, on_delete=models.CASCADE)
    default_tied_status = models.ForeignKey(
        TiedStatus, null=True, blank=True, default=None,
        on_delete=models.CASCADE)
    scope = models.ForeignKey(
        ActivityScope, null=True, blank=True, default=None,
        on_delete=models.CASCADE)

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
        fields=('title', 'description'),  # fields on the model
        config='pg_catalog.simple',  # default dictionary to use
        search_field='text',  # text field for all search fields,
        # TODO: make this compatible with M2M - 2016-01-11:
        auto_update_search_field=False,
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
            if (
                transaction.provider_organisation
                and transaction.provider_organisation.provider_activity
            ):
                providing_activities.append(
                    transaction.provider_organisation.provider_activity.id
                )

        return Activity.objects.filter(
            id__in=providing_activities
        ).exclude(id=self.id).distinct()

    @property
    def get_provided_activities(self):
        return Activity.objects.filter(
            transaction__provider_organisation__provider_activity=self.id
        ).exclude(
            id=self.id
        ).distinct()


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
    interest_payment_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        db_index=True,
    )
    interest_payment_currency = models.CharField(
        max_length=3,
        null=True,
        default=None,
        blank=True,
    )
    loan_repayment_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        db_index=True,
    )
    loan_repayment_currency = models.CharField(
        max_length=3,
        null=True,
        default=None,
        blank=True,
    )
    reimbursement_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        db_index=True,
    )
    reimbursement_currency = models.CharField(
        max_length=3,
        null=True,
        default=None,
        blank=True,
    )
    purchase_of_equity_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        db_index=True,
    )
    purchase_of_equity_currency = models.CharField(
        max_length=3,
        null=True,
        default=None,
        blank=True,
    )
    sale_of_equity_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        db_index=True,
    )
    sale_of_equity_currency = models.CharField(
        max_length=3,
        null=True,
        default=None,
        blank=True,
    )
    credit_guarantee_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        db_index=True,
    )
    credit_guarantee_currency = models.CharField(
        max_length=3,
        null=True,
        default=None,
        blank=True,
    )
    incoming_commitment_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        db_index=True,
    )
    incoming_commitment_currency = models.CharField(
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
            ["interest_payment_value", "activity"],
            ["loan_repayment_value", "activity"],
            ["reimbursement_value", "activity"],
            ["purchase_of_equity_value", "activity"],
            ["sale_of_equity_value", "activity"],
            ["credit_guarantee_value", "activity"],
            ["incoming_commitment_value", "activity"]
        ]


class ActivityAggregation(AbstractActivityAggregation):
    activity = models.OneToOneField(
        Activity, related_name="activity_aggregation",
        default=None, on_delete=models.CASCADE)


class ChildAggregation(AbstractActivityAggregation):
    activity = models.OneToOneField(
        Activity, related_name="child_aggregation", default=None,
        on_delete=models.CASCADE)


class ActivityPlusChildAggregation(AbstractActivityAggregation):
    activity = models.OneToOneField(
        Activity,
        related_name="activity_plus_child_aggregation",
        default=None, on_delete=models.CASCADE)


class Title(models.Model):
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    # related name allows title to be accessed from activity.title
    activity = models.OneToOneField(Activity, related_name="title",
                                    on_delete=models.CASCADE)

    def get_activity(self):
        return self.activity

    def __unicode__(self,):
        return "Title"


class ActivitySearchData(models.Model):
    activity = models.OneToOneField(Activity, on_delete=models.CASCADE)
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
    normalized_ref = models.CharField(
        max_length=120, db_index=True, default="", blank=True)

    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    activity = models.ForeignKey(
        Activity,
        related_name="reporting_organisations", on_delete=models.CASCADE)

    # if in organisation standard
    organisation = models.ForeignKey(
        Organisation,
        null=True,
        default=None,
        on_delete=models.SET_NULL)
    type = models.ForeignKey(
        OrganisationType, null=True, default=None, blank=True,
        on_delete=models.CASCADE
    )

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
    normalized_ref = models.CharField(
        blank=True,
        max_length=120,
        null=True,
        default=None,
        db_index=True)

    activity = models.ForeignKey(
        Activity,
        related_name="participating_organisations", on_delete=models.CASCADE)

    # if in organisation standard
    organisation = models.ForeignKey(
        Organisation,
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET_NULL)

    type = models.ForeignKey(OrganisationType,
                             null=True, blank=True,
                             default=None, on_delete=models.CASCADE)
    role = models.ForeignKey(OrganisationRole,
                             null=True, blank=True,
                             default=None, on_delete=models.CASCADE)

    # when organisation is not mentioned in transactions
    org_activity_id = models.CharField(
        max_length=150, blank=False, null=True, db_index=True)
    org_activity_obj = models.ForeignKey(
        Activity,
        related_name="participating_activity",
        null=True,
        default=None, on_delete=models.CASCADE)

    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    # TODO: Workaround for IATI ref limitation - 2015-11-26
    primary_name = models.TextField(blank=True)

    crs_channel_code = models.ForeignKey(
        CRSChannelCode,
        null=True,
        on_delete=models.CASCADE
    )

    def __unicode__(self,):
        return "name: %s - role: %s" % (self.primary_name, self.role)

    class Meta:
        verbose_name = 'Participating organisation'
        verbose_name_plural = 'Participating organisations'

    def get_activity(self):
        return self.activity


class ActivityPolicyMarker(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    code = models.ForeignKey(PolicyMarker, on_delete=models.CASCADE)
    vocabulary = models.ForeignKey(PolicyMarkerVocabulary,
                                   on_delete=models.CASCADE)
    vocabulary_uri = models.URLField(null=True, blank=True)
    significance = models.ForeignKey(
        PolicySignificance,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    def __unicode__(self,):
        return "code: %s - significance: %s" % (
            self.code, self.significance.code
        )

    class Meta:
        verbose_name = 'Policy marker'
        verbose_name_plural = 'Policy markers'

    def get_activity(self):
        return self.activity


class ActivitySector(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE)
    vocabulary = models.ForeignKey(SectorVocabulary,
                                   null=True, blank=True,
                                   default=None, on_delete=models.CASCADE)
    vocabulary_uri = models.URLField(null=True, blank=True)
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        default=None)

    def __unicode__(self,):
        return "name: %s" % self.sector.name

    class Meta:
        verbose_name = 'Sector'
        verbose_name_plural = 'Sectors'

    def get_activity(self):
        return self.activity


class ActivityRecipientCountry(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
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
    activity = models.OneToOneField(
        Activity, related_name="country_budget_items",
        on_delete=models.CASCADE)
    vocabulary = models.ForeignKey(BudgetIdentifierVocabulary,
                                   on_delete=models.CASCADE)

    def get_activity(self):
        return self.activity


class HumanitarianScope(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    code = models.CharField(max_length=100)
    vocabulary = models.ForeignKey(HumanitarianScopeVocabulary,
                                   on_delete=models.CASCADE)
    vocabulary_uri = models.URLField(null=True, blank=True)
    type = models.ForeignKey(HumanitarianScopeType, on_delete=models.CASCADE)

    def get_activity(self):
        return self.activity


class BudgetItem(models.Model):
    country_budget_item = models.ForeignKey(CountryBudgetItem,
                                            on_delete=models.CASCADE)
    code = models.ForeignKey(BudgetIdentifier, on_delete=models.CASCADE)
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        default=None)

    def get_activity(self):
        return self.country_budget_item.activity


class BudgetItemDescription(models.Model):
    budget_item = models.OneToOneField(
        BudgetItem, related_name="description", on_delete=models.CASCADE)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    def get_activity(self):
        return self.budget_item.country_budget_item.activity


class ActivityRecipientRegion(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    vocabulary = models.ForeignKey(
        RegionVocabulary, default=1, on_delete=models.CASCADE)
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
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    identifier = models.CharField(max_length=100)
    owner_ref = models.CharField(max_length=100, default="")
    # owner_name = models.CharField(max_length=100, default="")
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')
    type = models.ForeignKey(
        OtherIdentifierType, null=True, blank=True, on_delete=models.CASCADE)

    def __unicode__(self,):
        return "identifier: %s" % self.identifier

    def get_activity(self):
        return self.activity


class ActivityWebsite(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    url = models.URLField()

    def __unicode__(self,):
        return "%s" % self.url

    def get_activity(self):
        return self.activity


class ContactInfo(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    type = models.ForeignKey(
        ContactType, null=True, blank=True, on_delete=models.CASCADE)
    telephone = models.CharField(
        max_length=100, default="", null=True, blank=True)
    email = models.TextField(default="", null=True, blank=True)
    website = models.CharField(
        max_length=255, default="", null=True, blank=True)

    def __unicode__(self,):
        return "type: %s" % self.type

    def get_activity(self):
        return self.activity


class ContactInfoOrganisation(models.Model):
    contact_info = models.OneToOneField(
        ContactInfo, related_name="organisation",
        default=None, on_delete=models.CASCADE)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')


class ContactInfoDepartment(models.Model):
    contact_info = models.OneToOneField(
        ContactInfo, related_name="department",
        default=None, on_delete=models.CASCADE)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    def get_activity(self):
        return self.contact_info.activity


class ContactInfoPersonName(models.Model):
    contact_info = models.OneToOneField(
        ContactInfo, related_name="person_name",
        default=None, on_delete=models.CASCADE)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    def get_activity(self):
        return self.contact_info.activity


class ContactInfoJobTitle(models.Model):
    contact_info = models.OneToOneField(
        ContactInfo, related_name="job_title",
        default=None, on_delete=models.CASCADE)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    def get_activity(self):
        return self.contact_info.activity


class ContactInfoMailingAddress(models.Model):
    contact_info = models.OneToOneField(
        ContactInfo, related_name="mailing_address",
        default=None, on_delete=models.CASCADE)
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
        default=None, on_delete=models.CASCADE)
    ref = models.CharField(db_index=True, max_length=200,
                           default="", blank=True)

    def __unicode__(self,):
        return "ref-activity: %s" % self.ref_activity

    class Meta:
        verbose_name_plural = "related activities"

    def get_activity(self):
        return self.current_activity


class DocumentLink(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    result = models.ForeignKey('Result', null=True, on_delete=models.CASCADE)
    result_indicator = models.ForeignKey(
        'ResultIndicator',
        related_name='result_indicator_document_links',
        null=True,
        on_delete=models.CASCADE
    )
    # XXX: could also point to a separate 'Basline' model that should come up
    # from ResultIndicator model:
    result_indicator_baseline = models.ForeignKey(
        'ResultIndicator',
        related_name='baseline_document_links',
        null=True,
        on_delete=models.CASCADE
    )
    period_target = models.ForeignKey(
        'ResultIndicator',
        related_name='period_target_document_links',
        null=True,
        on_delete=models.CASCADE
    )
    period_actual = models.ForeignKey(
        'ResultIndicator',
        related_name='period_actual_document_links',
        null=True,
        on_delete=models.CASCADE
    )
    url = models.TextField(max_length=500)
    file_format = models.ForeignKey(
        FileFormat, null=True, blank=True,
        default=None, on_delete=models.CASCADE)
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
    document_link = models.ForeignKey(DocumentLink, on_delete=models.CASCADE)
    category = models.ForeignKey(DocumentCategory, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Document link categories"

    def get_activity(self):
        return self.document_link.activity


class DocumentLinkLanguage(models.Model):
    document_link = models.ForeignKey(DocumentLink, on_delete=models.CASCADE)
    language = models.ForeignKey(
        Language, null=True, blank=True,
        default=None, on_delete=models.CASCADE)

    def get_activity(self):
        return self.document_link.activity


class DocumentLinkTitle(models.Model):
    document_link = models.OneToOneField(
        DocumentLink, on_delete=models.CASCADE)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    def get_activity(self):
        return self.document_link.activity


class DocumentSearch(models.Model):
    '''Currently this model is just stored for refference and searching (both
    feature and API endpoint) for Documents is disabled
    '''
    document = models.OneToOneField('Document', on_delete=models.CASCADE)
    content = VectorField()
    text = VectorField()
    last_reindexed = models.DateTimeField()


class Document(models.Model):
    document_link = models.OneToOneField(
        DocumentLink, on_delete=models.CASCADE)
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
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    type = models.ForeignKey(
        ResultType, null=True, blank=True,
        default=None, on_delete=models.CASCADE)
    aggregation_status = models.BooleanField(default=False)

    def __unicode__(self,):
        return "Result"

    def get_activity(self):
        return self.activity


class ResultTitle(models.Model):
    result = models.OneToOneField(Result, on_delete=models.CASCADE)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    def get_activity(self):
        return self.result.activity


class ResultDescription(models.Model):
    result = models.OneToOneField(Result, on_delete=models.CASCADE)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    def get_activity(self):
        return self.result.activity


class ResultIndicator(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE)
    baseline_year = models.IntegerField(null=True, blank=True, default=None)
    baseline_value = models.CharField(
        null=True, blank=True, default=None, max_length=100)
    measure = models.ForeignKey(
        IndicatorMeasure,
        null=True,
        blank=True,
        default=None, on_delete=models.CASCADE)
    ascending = models.BooleanField(default=True)
    aggregation_status = models.BooleanField(default=False)

    def get_activity(self):
        return self.result.activity

    def __unicode__(self,):
        return "baseline year: %s" % self.baseline_year


class ResultReference(models.Model):
    result = models.ForeignKey(
        Result, on_delete=models.CASCADE)
    code = models.CharField(max_length=255)
    vocabulary = models.ForeignKey(
        ResultVocabulary, on_delete=models.CASCADE)
    vocabulary_uri = models.URLField(null=True, blank=True)

    def get_activity(self):
        return self.result.activity


class ResultIndicatorReference(models.Model):
    result_indicator = models.ForeignKey(
        ResultIndicator, on_delete=models.CASCADE)
    code = models.CharField(max_length=255)
    vocabulary = models.ForeignKey(
        IndicatorVocabulary, on_delete=models.CASCADE)
    # TODO: this should be renamed to vocabulary_uri in IATI standard...
    # - 2016-06-03:
    indicator_uri = models.URLField(null=True, blank=True)

    def get_activity(self):
        return self.result_indicator.result.activity


class ResultIndicatorTitle(models.Model):
    result_indicator = models.OneToOneField(
        ResultIndicator, on_delete=models.CASCADE)
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
    result_indicator = models.OneToOneField(
        ResultIndicator, on_delete=models.CASCADE)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    def get_activity(self):
        return self.result_indicator.result.activity


class ResultIndicatorBaselineComment(models.Model):
    result_indicator = models.OneToOneField(
        ResultIndicator, on_delete=models.CASCADE)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    def get_activity(self):
        return self.result_indicator.result.activity


class ResultIndicatorPeriod(models.Model):
    result_indicator = models.ForeignKey(
        ResultIndicator, on_delete=models.CASCADE)
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)

    # XXX: Previous relationship:
    # target = models.DecimalField(
        # max_digits=25, decimal_places=10, null=True, blank=True)
    actual = models.DecimalField(
        max_digits=25, decimal_places=10, null=True, blank=True)

    def __unicode__(self,):
        return "target: %s, actual: %s" % (
            self.target.value if self.target else 'none',
            self.actual
        )

    def get_activity(self):
        return self.result_indicator.result.activity


class ResultIndicatorPeriodTarget(models.Model):
    value = models.CharField(
        max_length=50, blank=True, default='')
    result_indicator_period = models.ForeignKey(
        ResultIndicatorPeriod,
        null=True,
        related_name='targets',
        on_delete=models.CASCADE
    )

    def __unicode__(self,):
        return "target: %s" % (self.value)


class ResultIndicatorPeriodTargetLocation(models.Model):
    result_indicator_period_target = models.ForeignKey(
        ResultIndicatorPeriodTarget, on_delete=models.CASCADE)
    ref = models.CharField(max_length=50)
    location = models.ForeignKey('Location', on_delete=models.CASCADE)

    def __unicode__(self,):
        return "%s" % self.ref

    # FIXME: fix all these at least on ResultIndicators
    def get_activity(self):
        return self.result_indicator_period.result_indicator.result.activity


class ResultIndicatorPeriodActualLocation(models.Model):
    result_indicator_period = models.ForeignKey(
        ResultIndicatorPeriod, on_delete=models.CASCADE)
    ref = models.CharField(max_length=50)
    location = models.ForeignKey('Location', on_delete=models.CASCADE)

    def __unicode__(self,):
        return "%s" % self.ref

    def get_activity(self):
        return self.result_indicator_period.result_indicator.result.activity


class ResultIndicatorPeriodTargetDimension(models.Model):
    result_indicator_period = models.ForeignKey(
        ResultIndicatorPeriod, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

    def __unicode__(self,):
        return "%s: %s" % (self.name, self.value)

    def get_activity(self):
        return self.result_indicator_period.result_indicator.result.activity


class ResultIndicatorPeriodActualDimension(models.Model):
    result_indicator_period = models.ForeignKey(
        ResultIndicatorPeriod, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

    def __unicode__(self,):
        return "%s: %s" % (self.name, self.value)

    def get_activity(self):
        return self.result_indicator_period.result_indicator.result.activity


class ResultIndicatorBaselineDimension(models.Model):
    result_indicator = models.ForeignKey(
        ResultIndicator, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

    def __unicode__(self,):
        return "%s: %s" % (self.name, self.value)

    def get_activity(self):
        return self.result_indicator.result.activity


class ResultIndicatorPeriodTargetComment(models.Model):
    result_indicator_period_target = models.ForeignKey(
        ResultIndicatorPeriodTarget, on_delete=models.CASCADE)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    def get_activity(self):
        return self.result_indicator_period.result_indicator.result.activity


class ResultIndicatorPeriodActualComment(models.Model):
    result_indicator_period = models.OneToOneField(
        ResultIndicatorPeriod, on_delete=models.CASCADE)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    def get_activity(self):
        return self.result_indicator_period.result_indicator.result.activity


class Description(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
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
        default=None, on_delete=models.CASCADE)

    def __unicode__(self,):
        return "Description with type %s" % self.type

    def get_activity(self):
        return self.activity


class Budget(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    type = models.ForeignKey(
        BudgetType, null=True, blank=True,
        default=None, on_delete=models.CASCADE)
    status = models.ForeignKey(
        BudgetStatus, default=1, on_delete=models.CASCADE)
    period_start = models.DateField(blank=True, default=None)
    period_end = models.DateField(blank=True, default=None)
    value = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True)
    value_string = models.CharField(max_length=50)
    value_date = models.DateField(null=True, blank=True, default=None)
    currency = models.ForeignKey(
        Currency, null=True, blank=True,
        default=None, on_delete=models.CASCADE)

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

    def __unicode__(self,):
        return "value: %s - period_start: %s - period_end: %s" % (
            str(self.value), self.period_start, self.period_end)

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

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    type = models.ForeignKey(
        BudgetType, null=True, blank=True,
        default=None, on_delete=models.CASCADE)
    period_start = models.DateField(blank=True, default=None)
    period_end = models.DateField(null=True, blank=True, default=None)
    value = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True)
    value_string = models.CharField(max_length=50)
    value_date = models.DateField(null=True, blank=True, default=None)
    currency = models.ForeignKey(
        Currency, null=True, blank=True,
        default=None, on_delete=models.CASCADE)

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

    def __unicode__(self,):
        return "value: %s - period_start: %s - period_end: %s" % (
            str(self.value), self.period_start, self.period_end)

    def get_activity(self):
        return self.activity


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
        blank=True,
        on_delete=models.CASCADE
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
        blank=True,
        on_delete=models.CASCADE
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

    def get_activity(self):
        return self.planned_disbursement.activity


class Conditions(models.Model):
    activity = models.OneToOneField(
        Activity, related_name="conditions", on_delete=models.CASCADE)
    attached = models.BooleanField()

    def get_activity(self):
        return self.activity


class Condition(models.Model):
    conditions = models.ForeignKey(Conditions, on_delete=models.CASCADE)
    type = models.ForeignKey(
        ConditionType, null=True, blank=True,
        default=None, on_delete=models.CASCADE)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    def get_activity(self):
        return self.conditions.activity


class Location(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    result_indicator_baseline = models.ForeignKey(
        ResultIndicator,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='baseline_locations',
    )

    ref = models.CharField(max_length=200, default="", null=True, blank=True)
    location_reach = models.ForeignKey(
        GeographicLocationReach,
        null=True,
        blank=True,
        default=None,
        related_name="location_reach", on_delete=models.CASCADE)

    # TODO: make location_id a one-to-one field?
    location_id_vocabulary = models.ForeignKey(
        GeographicVocabulary,
        null=True,
        blank=True,
        default=None,
        related_name="location_id_vocabulary",
        on_delete=models.CASCADE)
    location_id_code = models.CharField(blank=True, max_length=255, default="")

    location_class = models.ForeignKey(
        GeographicLocationClass,
        null=True,
        blank=True,
        default=None, on_delete=models.CASCADE)
    feature_designation = models.ForeignKey(
        LocationType,
        null=True,
        blank=True,
        default=None,
        related_name="feature_designation", on_delete=models.CASCADE)

    point_srs_name = models.CharField(blank=True, max_length=255, default="")
    point_pos = PointField(
        null=True,
        blank=False,
        default=None,
        spatial_index=True,
        srid=4326,
        geography=True)
    exactness = models.ForeignKey(
        GeographicExactness, null=True, blank=True,
        default=None, on_delete=models.CASCADE)

    objects = LocationManager()

    def __unicode__(self,):
        return "Location: %s" % self.point_pos

    def get_activity(self):
        return self.activity


# TODO: move to codelist
class LocationAdministrative(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    code = models.CharField(max_length=255)
    vocabulary = models.ForeignKey(
        GeographicVocabulary,
        related_name="administrative_vocabulary", on_delete=models.CASCADE)
    level = models.IntegerField(null=True, blank=True, default=None)

    def get_activity(self):
        return self.location.activity


class LocationName(models.Model):
    location = models.OneToOneField(
        Location, related_name="name", on_delete=models.CASCADE)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    def get_activity(self):
        return self.location.activity


class LocationDescription(models.Model):
    location = models.OneToOneField(
        Location, related_name="description", on_delete=models.CASCADE)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    def get_activity(self):
        return self.location.activity


class LocationActivityDescription(models.Model):
    location = models.OneToOneField(
        Location, related_name="activity_description",
        on_delete=models.CASCADE)
    narratives = GenericRelation(
        Narrative,
        content_type_field='related_content_type',
        object_id_field='related_object_id')

    def get_activity(self):
        return self.location.activity


class Fss(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    extraction_date = models.DateField()
    priority = models.BooleanField(default=False)
    phaseout_year = models.IntegerField(null=True, blank=True)

    def __unicode__(self,):
        return "%s" % self.extraction_date

    def get_activity(self):
        return self.activity


class FssForecast(models.Model):
    fss = models.ForeignKey(Fss, on_delete=models.CASCADE)
    year = models.IntegerField()
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    value_date = models.DateField()
    value = models.DecimalField(max_digits=15, decimal_places=2)

    def __unicode__(self,):
        return "%s" % self.year

    def get_activity(self):
        return self.fss.activity


class CrsAdd(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    channel_code = models.CharField(max_length=50, null=True, blank=True)

    def __unicode__(self,):
        return "%s" % self.id

    def get_activity(self):
        return self.activity


class CrsAddOtherFlags(models.Model):
    crs_add = models.ForeignKey(
        CrsAdd, related_name="other_flags", on_delete=models.CASCADE)
    other_flags = models.ForeignKey(OtherFlags, on_delete=models.CASCADE)
    significance = models.BooleanField()

    def __unicode__(self,):
        return "%s" % self.id

    def get_activity(self):
        return self.crs_add.activity


class CrsAddLoanTerms(models.Model):
    crs_add = models.OneToOneField(
        CrsAdd, related_name="loan_terms", on_delete=models.CASCADE)
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
        default=None, on_delete=models.CASCADE)
    repayment_plan = models.ForeignKey(
        LoanRepaymentPeriod,
        null=True,
        blank=True,
        default=None, on_delete=models.CASCADE)
    repayment_plan_text = models.TextField(null=True, blank=True, default="")
    commitment_date = models.DateField(null=True, blank=True, default=None)
    repayment_first_date = models.DateField(
        null=True, blank=True, default=None)
    repayment_final_date = models.DateField(
        null=True, blank=True, default=None)

    def __unicode__(self,):
        return "%s" % self.crs_add_id

    def get_activity(self):
        return self.crs_add.activity


class CrsAddLoanStatus(models.Model):
    crs_add = models.OneToOneField(
        CrsAdd, related_name="loan_status", on_delete=models.CASCADE)
    year = models.IntegerField(null=True, blank=True, default=None)
    value_date = models.DateField(null=True, blank=True, default=None)
    currency = models.ForeignKey(
        Currency, null=True, blank=True,
        default=None, on_delete=models.CASCADE)
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
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    iso_date = models.DateField()
    type = models.ForeignKey(ActivityDateType, on_delete=models.CASCADE)

    def __unicode__(self):
        return "type: %s - iso_date: %s" % (
            self.type, self.iso_date.strftime('%Y-%m-%d')
        )

    def get_activity(self):
        return self.activity


class LegacyData(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, null=True, blank=True)
    value = models.CharField(max_length=200, null=True, blank=True)
    iati_equivalent = models.CharField(max_length=150, null=True, blank=True)

    def __unicode__(self):
        return "%s" % self.name

    def get_activity(self):
        return self.activity


class ActivityTag(models.Model):
    """A model to store Tags on Activity (introduced in 2.03)
    Actual tag values are stored in Narrative model:

        Narrative.objects.filter(
            related_content_type__model='activitytag',
            activity=activity_model_instance,
        ).values_list('content')

    In the future (if needed), implement a separate field for storing tag value
    or s separate method (get_tag_value) to get it from Narratives or smth.
    """
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    code = models.CharField(max_length=5)
    vocabulary = models.ForeignKey(
        TagVocabulary, on_delete=models.CASCADE
    )
    vocabulary_uri = models.URLField(blank=True)

    def __str__(self):
        return "tag for %s" % self.activity
