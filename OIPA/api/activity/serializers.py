from rest_framework import serializers

from iati import models as iati_models
from api.generics.serializers import DynamicFieldsSerializer
from api.generics.serializers import DynamicFieldsModelSerializer
from api.generics.fields import PointField
from api.sector.serializers import SectorSerializer
from api.region.serializers import RegionSerializer
from api.country.serializers import CountrySerializer
from api.activity.filters import RelatedActivityFilter

from api.codelist.serializers import VocabularySerializer
from api.codelist.serializers import CodelistSerializer
from api.codelist.serializers import NarrativeContainerSerializer
from api.codelist.serializers import NarrativeSerializer
from api.codelist.serializers import CodelistCategorySerializer


class ValueSerializer(serializers.Serializer):
    currency = CodelistSerializer()
    date = serializers.CharField(source='value_date')
    value = serializers.DecimalField(
            max_digits=15,
            decimal_places=2,
            coerce_to_string=False,
            )

    class Meta:
        fields = (
                'value',
                'date',
                'currency',
                )


class DocumentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = iati_models.DocumentCategory
        fields = ('code', 'name')


class DocumentLinkSerializer(serializers.ModelSerializer):

    class DocumentDateSerializer(serializers.Serializer):
        iso_date = serializers.DateField(source='iso_date')

    format = CodelistSerializer(source='file_format')
    categories = DocumentCategorySerializer(many=True)
    title = NarrativeContainerSerializer(source="documentlinktitle")
    document_date = DocumentDateSerializer(source="iso_date")

    class Meta:
        model = iati_models.DocumentLink
        fields = (
            'url',
            'format',
            'categories',
            'title',
            'document_date',
        )


class CapitalSpendSerializer(serializers.ModelSerializer):
    percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        source='*',
        coerce_to_string=False
    )

    class Meta:
        model = iati_models.Activity
        fields = ('percentage',)


class BudgetSerializer(serializers.ModelSerializer):

    value = ValueSerializer(source='*')
    type = CodelistSerializer()
    status = CodelistSerializer()

    class Meta:
        model = iati_models.Budget
        # filter_class = BudgetFilter
        fields = (
            'type',
            'status',
            'period_start',
            'period_end',
            'value',
        )

class PlannedDisbursementSerializer(serializers.ModelSerializer):
    value = ValueSerializer(source='*')
    type = CodelistSerializer()

    class Meta:
        model = iati_models.PlannedDisbursement

        fields = (
            'type',
            'period_start',
            'period_end',
            'value',
        )


class ActivityDateSerializer(serializers.Serializer):
    type = CodelistSerializer()
    iso_date = serializers.DateTimeField()

    class Meta:
        model = iati_models.ActivityDate
        fields = ('iso_date', 'type')


class ActivityAggregationSerializer(DynamicFieldsSerializer):
    budget_value = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False)
    budget_currency = serializers.CharField()
    disbursement_value = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False)
    disbursement_currency = serializers.CharField()
    incoming_funds_value = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False)
    incoming_funds_currency = serializers.CharField()
    commitment_value = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False)
    commitment_currency = serializers.CharField()
    expenditure_value = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False)
    expenditure_currency = serializers.CharField()


class ReportingOrganisationSerializer(DynamicFieldsModelSerializer):
    # TODO: Link to organisation standard (hyperlinked)
    ref = serializers.CharField(source="normalized_ref")
    type = CodelistSerializer()
    secondary_reporter = serializers.BooleanField()
    narratives = NarrativeSerializer(many=True)
    # organisation = OrganisationSerializer()
    organisation = serializers.HyperlinkedRelatedField(view_name='organisations:organisation-detail', read_only=True)

    class Meta:
        model = iati_models.ActivityReportingOrganisation
        fields = (
            'ref',
            'organisation',
            'type',
            'secondary_reporter',
            'narratives',
        )

class ParticipatingOrganisationSerializer(serializers.ModelSerializer):
    # TODO: Link to organisation standard (hyperlinked)
    ref = serializers.CharField(source='normalized_ref')
    type = CodelistSerializer()
    role = CodelistSerializer()
    activity_id = serializers.CharField(source='org_activity_id')
    narratives = NarrativeSerializer(many=True)

    class Meta:
        model = iati_models.ActivityParticipatingOrganisation
        fields = (
            'ref',
            'type',
            'role',
            'activity_id',
            'narratives',
        )

class ActivityPolicyMarkerSerializer(serializers.ModelSerializer):
    code = CodelistSerializer()
    vocabulary = VocabularySerializer()
    vocabulary_uri = serializers.URLField()
    significance = CodelistSerializer()
    narratives = NarrativeSerializer(many=True)

    class Meta:
        model = iati_models.ActivityPolicyMarker
        fields = (
            'narratives',
            'vocabulary',
            'vocabulary_uri',
            'significance',
            'code',
        )


# TODO: change to NarrativeContainer
class TitleSerializer(serializers.Serializer):
    narratives = NarrativeSerializer(many=True)

    class Meta:
        model = iati_models.Title
        fields = ('narratives',)

class DescriptionSerializer(serializers.ModelSerializer):
    type = CodelistSerializer()
    narratives = NarrativeSerializer(many=True)

    class Meta:
        model = iati_models.Description
        fields = (
            'type',
            'narratives'
        )

class RelatedActivityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = iati_models.RelatedActivityType
        fields = (
            'code',
            'name'
        )

class RelatedActivitySerializer(serializers.ModelSerializer):
    ref_activity = serializers.HyperlinkedRelatedField(view_name='activities:activity-detail', read_only=True)
    type = RelatedActivityTypeSerializer()

    class Meta:
        model = iati_models.RelatedActivity
        filter_class = RelatedActivityFilter
        fields = (
            'ref_activity',
            'ref',
            'type',
        )

class ActivitySectorSerializer(serializers.ModelSerializer):
    sector = SectorSerializer(fields=('url', 'code', 'name'))
    percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        coerce_to_string=False
    )
    vocabulary = VocabularySerializer()
    vocabulary_uri = serializers.URLField()

    class Meta:
        model = iati_models.ActivitySector
        fields = (
            'sector',
            'percentage',
            'vocabulary',
            'vocabulary_uri',
        )


class ActivitySectorSerializer(serializers.ModelSerializer):
    sector = SectorSerializer(fields=('url', 'code', 'name'))
    percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        coerce_to_string=False
    )
    vocabulary = VocabularySerializer()
    vocabulary_uri = serializers.URLField()

    class Meta:
        model = iati_models.ActivitySector
        fields = (
            'sector',
            'percentage',
            'vocabulary',
            'vocabulary_uri',
        )

class ActivityRecipientRegionSerializer(DynamicFieldsModelSerializer):
    region = RegionSerializer(
        fields=('url', 'code', 'name')
    )
    percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        coerce_to_string=False
    )
    vocabulary = VocabularySerializer()
    vocabulary_uri = serializers.URLField()

    class Meta:
        model = iati_models.ActivityRecipientRegion
        fields = (
            'region',
            'percentage',
            'vocabulary',
            'vocabulary_uri',
        )

class HumanitarianScopeSerializer(DynamicFieldsModelSerializer):
    type = CodelistSerializer() 
    vocabulary = VocabularySerializer()
    vocabulary_uri = serializers.URLField()
    code = CodelistSerializer()

    class Meta:
        model = iati_models.HumanitarianScope
        fields = (
            'type',
            'vocabulary',
            'vocabulary_uri',
            'code',
        )

class RecipientCountrySerializer(DynamicFieldsModelSerializer):
    country = CountrySerializer(fields=('url', 'code', 'name'))
    percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        coerce_to_string=False
    )
    # vocabulary = VocabularySerializer()

    class Meta:
        model = iati_models.ActivityRecipientCountry
        fields = (
            'country',
            'percentage',
        )


class ResultTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = iati_models.ResultType
        fields = (
            'code',
            'name',
        )

class ResultDescriptionSerializer(serializers.ModelSerializer):
    narratives = NarrativeSerializer(source="*")

    class Meta:
        model = iati_models.ResultDescription
        fields = (
            'narratives',
        )

class ResultTitleSerializer(serializers.ModelSerializer):
    narratives = NarrativeSerializer(source="*")

    class Meta:
        model = iati_models.ResultTitle
        fields = (
            'narratives',
        )



class ResultIndicatorPeriodLocationSerializer(serializers.Serializer):
    ref = serializers.CharField()

    class Meta:
        fields = (
            'ref',
        )

class ResultIndicatorPeriodDimensionSerializer(serializers.Serializer):
    name = serializers.CharField()
    value = serializers.DecimalField(
        max_digits=25,
        decimal_places=10,
        coerce_to_string=False)

    class Meta:
        fields = (
            'name',
            'value',
        )

class ResultIndicatorPeriodTargetSerializer(serializers.Serializer):
    value = serializers.CharField(source='target')
    comment = NarrativeContainerSerializer(source="resultindicatorperiodtargetcomment")
    location = ResultIndicatorPeriodLocationSerializer(many=True, source="resultindicatorperiodtargetlocation_set")
    dimension = ResultIndicatorPeriodDimensionSerializer(many=True, source="resultindicatorperiodtargetdimension_set")

class ResultIndicatorPeriodActualSerializer(serializers.Serializer):
    value = serializers.CharField(source='actual')
    comment = NarrativeContainerSerializer(source="resultindicatorperiodactualcomment")
    location = ResultIndicatorPeriodLocationSerializer(many=True, source="resultindicatorperiodactuallocation_set")
    dimension = ResultIndicatorPeriodDimensionSerializer(many=True, source="resultindicatorperiodactualdimension_set")

class ResultIndicatorPeriodSerializer(serializers.ModelSerializer):
    target = ResultIndicatorPeriodTargetSerializer(source="*")
    actual = ResultIndicatorPeriodActualSerializer(source="*")

    class Meta:
        model = iati_models.ResultIndicatorPeriod
        fields = (
            'period_start',
            'period_end',
            'target',
            'actual',
        )

class ResultIndicatorBaselineSerializer(serializers.Serializer):
    year = serializers.CharField(source='baseline_year')
    value = serializers.CharField(source='baseline_value')
    comment = NarrativeContainerSerializer(source="resultindicatorbaselinecomment")

class ResultIndicatorSerializer(serializers.ModelSerializer):
    title = NarrativeContainerSerializer(source="resultindicatortitle")
    description = NarrativeContainerSerializer(source="resultindicatordescription")
    #  TODO 2.02 reference = ? 
    baseline = ResultIndicatorBaselineSerializer(source="*")
    period = ResultIndicatorPeriodSerializer(source='resultindicatorperiod_set', many=True)
    measure = CodelistSerializer()

    class Meta:
        model = iati_models.ResultIndicator
        fields = (
            'title',
            'description',
            'baseline',
            'period',
            'measure',
            'ascending'
        )


class ContactInfoSerializer(serializers.ModelSerializer):
    type = CodelistSerializer()
    organisation = NarrativeContainerSerializer()
    department = NarrativeContainerSerializer()
    person_name = NarrativeContainerSerializer()
    job_title = NarrativeContainerSerializer()
    mailing_address = NarrativeContainerSerializer()

    class Meta:
        model = iati_models.ContactInfo
        fields = (
            'type',
            'organisation',
            'department',
            'person_name',
            'job_title',
            'telephone',
            'email',
            'website',
            'mailing_address',
        )

class ResultSerializer(serializers.ModelSerializer):
    type = CodelistSerializer() 
    title = NarrativeContainerSerializer(source="resulttitle")
    description = NarrativeContainerSerializer(source="resultdescription")
    indicator = ResultIndicatorSerializer(source='resultindicator_set', many=True)

    class Meta:
        model = iati_models.Result
        fields = (
            'title',
            'description',
            'indicator',
            'type',
            'aggregation_status',
        )

class LocationSerializer(serializers.ModelSerializer):
    class LocationIdSerializer(serializers.Serializer):
        vocabulary = VocabularySerializer(
            source='location_id_vocabulary')
        code = serializers.CharField(source='location_id_code')

    class PointSerializer(serializers.Serializer):
        pos = PointField(source='point_pos')
        srsName = serializers.CharField(source="point_srs_name")

    class AdministrativeSerializer(serializers.ModelSerializer):
        code = serializers.CharField()
        vocabulary = VocabularySerializer()

        class Meta:
            model = iati_models.LocationAdministrative
            fields = (
                'code',
                'vocabulary',
                'level',
            )

    location_reach = CodelistSerializer()
    location_id = LocationIdSerializer(source='*')
    name = NarrativeContainerSerializer(many=True, source="locationname_set")
    description = NarrativeContainerSerializer(many=True, source="locationdescription_set")
    activity_description = NarrativeContainerSerializer(many=True, source="locationactivitydescription_set")
    administrative = AdministrativeSerializer(many=True, source="locationadministrative_set")
    point = PointSerializer(source="*")
    exactness = CodelistSerializer()
    location_class = CodelistSerializer()
    feature_designation = CodelistCategorySerializer()
    
    class Meta:
        model = iati_models.Location
        fields = (
            'ref',
            'location_reach',
            'location_id',
            'name',
            'description',
            'activity_description',
            'administrative',
            'point',
            'exactness',
            'location_class',
            'feature_designation',
        )

class ActivityAggregationContainerSerializer(DynamicFieldsSerializer):
    activity = ActivityAggregationSerializer(source='activity_aggregation')
    children = ActivityAggregationSerializer(source='child_aggregation')
    activity_children = ActivityAggregationSerializer(source='activity_plus_child_aggregation')

class ActivitySerializer(DynamicFieldsModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='activities:activity-detail')
    iati_identifier = serializers.CharField()
    reporting_organisations = ReportingOrganisationSerializer(
        many=True,)
    title = TitleSerializer()
    descriptions = DescriptionSerializer(
        many=True, read_only=True, source='description_set')
    participating_organisations = ParticipatingOrganisationSerializer(
        many=True,)

    # TODO ; add other-identifier serializer
    # other_identifier = serializers.OtherIdentifierSerializer(many=True,source="?")

    activity_status = CodelistSerializer()
    activity_dates = ActivityDateSerializer(
        many=True,
        source='activitydate_set')

    # TODO ; add contact-info serializer
    # note; contact info has a sequence we should use in the ContactInfoSerializer!
    contact_info = ContactInfoSerializer(many=True,source="contactinfo_set")

    activity_scope = CodelistSerializer(source='scope')
    recipient_countries = RecipientCountrySerializer(
        many=True,
        source='activityrecipientcountry_set')
    recipient_regions = ActivityRecipientRegionSerializer(
        many=True,
        source='activityrecipientregion_set')
    locations = LocationSerializer(many=True, source='location_set')
    sectors = ActivitySectorSerializer(
        many=True,
        source='activitysector_set')

    # TODO ; add country-budget-items serializer
    # country_budget_items = serializers.CountryBudgetItemsSerializer(many=True,source="?")

    humanitarian_scope = HumanitarianScopeSerializer(many=True, source='humanitarianscope_set')

    policy_markers = ActivityPolicyMarkerSerializer(
        many=True,
        source='activitypolicymarker_set')
    collaboration_type = CodelistSerializer()
    default_flow_type = CodelistSerializer()
    default_finance_type = CodelistSerializer()
    default_aid_type = CodelistSerializer()
    default_tied_status = CodelistSerializer()

    budgets = BudgetSerializer(many=True, source='budget_set')

    # note; planned-disbursement has a sequence in PlannedDisbursementSerializer
    planned_disbursements = PlannedDisbursementSerializer(many=True, source='planneddisbursement_set')

    capital_spend = CapitalSpendSerializer()

    transactions = serializers.HyperlinkedIdentityField(
        view_name='activities:activity-transactions',)
    # transactions = TransactionSerializer(
    #     many=True,
    #     source='transaction_set')

    document_links = DocumentLinkSerializer(
        many=True,
        source='documentlink_set')
    related_activities = RelatedActivitySerializer(
        many=True, 
        source='relatedactivity_set')

    # TODO ; add legacy-data serializer? note: we dont parse legacy data atm.
    # legacy_data = LegacyDataSerializer(many=True, source="?")

    # TODO ; add conditions serializer
    # conditions = serializers.ConditionsSerializer(many=True,source="?")

    results = ResultSerializer(many=True, source="result_set")
    
    # TODO ; add crs-add serializer
    # note; crs-add has a sequence in CrsAddSerializer
    # crs_add = serializers.CrsAddSerializer(many=True, source="?")

    # TODO ; add fss serializer
    # fss = serializers.FssSerializer(many=True, source="?") 
    
    # activity attributes
    last_updated_datetime = serializers.DateTimeField()
    xml_lang = serializers.CharField(source='default_lang')
    default_currency = CodelistSerializer()

    humanitarian = serializers.BooleanField()

    # other added data
    aggregations = ActivityAggregationContainerSerializer(source="*")

    class Meta:
        model = iati_models.Activity
        fields = (
            'url',
            'id',
            'iati_identifier',
            'reporting_organisations',
            'title',
            'descriptions',
            'participating_organisations',
            # 'other_identifier',
            'activity_status',
            'activity_dates',
            'contact_info',
            'activity_scope',
            'recipient_countries',
            'recipient_regions',
            'locations',
            'sectors',
            # 'country_budget_items',
            'humanitarian',
            'humanitarian_scope',
            'policy_markers',
            'collaboration_type',
            'default_flow_type',
            'default_finance_type',
            'default_aid_type',
            'default_tied_status',
            'planned_disbursements',
            'budgets',
            'capital_spend',
            'transactions',
            'document_links',
            'related_activities',
            # 'legacy_data',
            # 'conditions',
            'results',
            # 'crs_add',
            # 'fss',
            'last_updated_datetime',
            'xml_lang',
            'default_currency',
            'humanitarian',
            'hierarchy',
            'linked_data_uri',
            'aggregations',
            'xml_source_ref',
        )

