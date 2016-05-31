from rest_framework import serializers

from iati import models as iati_models
from api.generics.serializers import DynamicFieldsSerializer
from api.generics.serializers import DynamicFieldsModelSerializer
from api.generics.fields import PointField
from api.sector.serializers import SectorSerializer
from api.organisation.serializers import OrganisationSerializer
from api.region.serializers import RegionSerializer
from api.country.serializers import CountrySerializer
from api.activity.filters import RelatedActivityFilter

from api.codelist.serializers import VocabularySerializer
from api.codelist.serializers import CodelistSerializer
from api.codelist.serializers import NarrativeContainerSerializer
from api.codelist.serializers import NarrativeSerializer
from api.codelist.serializers import CodelistCategorySerializer


class DocumentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = iati_models.DocumentCategory
        fields = ('code', 'name')


class DocumentLinkSerializer(serializers.ModelSerializer):
    format = CodelistSerializer(source='file_format')
    categories = DocumentCategorySerializer(many=True)
    title = NarrativeContainerSerializer(source="documentlinktitle_set", many=True)

    class Meta:
        model = iati_models.DocumentLink
        fields = (
            'url',
            'format',
            'categories',
            'title'
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
    class ValueSerializer(serializers.Serializer):
        currency = CodelistSerializer()
        date = serializers.CharField(source='value_date')
        value = serializers.DecimalField(
            max_digits=15,
            decimal_places=2,
            coerce_to_string=False,
        )

        class Meta:
            model = iati_models.Budget
            fields = (
                'value',
                'date',
                'currency',
            )

    value = ValueSerializer(source='*')
    type = CodelistSerializer()

    class Meta:
        model = iati_models.Budget
        # filter_class = BudgetFilter
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
    organisation = OrganisationSerializer()

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
    activity_id = serializers.HyperlinkedRelatedField(view_name='activities:activity-detail', source='org_activity_id', read_only=True)
    narratives = NarrativeSerializer(many=True)

    class Meta:
        model = iati_models.ActivityParticipatingOrganisation
        fields = (
            'ref',
            'type',
            'role',
            'activity_id'
            'narratives',
        )

class ActivityPolicyMarkerSerializer(serializers.ModelSerializer):
    code = CodelistSerializer()
    vocabulary = VocabularySerializer()
    significance = CodelistSerializer()
    narratives = NarrativeSerializer(many=True)

    class Meta:
        model = iati_models.ActivityPolicyMarker
        fields = (
            'narratives',
            'vocabulary',
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


class ResultIndicatorPeriodTargetSerializer(serializers.Serializer):
    # TODO 2.02 : location = 
    # TODO 2.02 : dimension = 
    value = serializers.CharField(source='target')
    comment = NarrativeContainerSerializer(source="resultindicatorperiodtargetcomment")

class ResultIndicatorPeriodActualSerializer(serializers.Serializer):
    # TODO 2.02 : location = 
    # TODO 2.02 : dimension = 
    value = serializers.CharField(source='actual')
    comment = NarrativeContainerSerializer(source="resultindicatorperiodactualcomment")

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
    # contact_info = serializers.ContactInfoSerializer(many=True,source="?")

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

    # TODO ; add humanitarian-scope serializer
    # humanitarian_scope = serializers.HumanitarianScopeSerializer(many=True,source="?")

    policy_markers = ActivityPolicyMarkerSerializer(
        many=True,
        source='activitypolicymarker_set')
    collaboration_type = CodelistSerializer()
    default_flow_type = CodelistSerializer()
    default_finance_type = CodelistSerializer()
    default_aid_type = CodelistSerializer()
    default_tied_status = CodelistSerializer()

    budgets = BudgetSerializer(many=True, source='budget_set')

    # TODO ; add planned-disbursement serializer
    # note; planned-disbursement has a sequence in PlannedDisbursementSerializer
    # planned_disbursement = serializers.PlannedDisbursementSerializer(many=True,source="?")

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
            # 'contact_info',
            'activity_scope',
            'recipient_countries',
            'recipient_regions',
            'locations',
            'sectors',
            # 'country_budget_items',
            # 'humanitarian_scope',
            'policy_markers',
            'collaboration_type',
            'default_flow_type',
            'default_finance_type',
            'default_aid_type',
            'default_tied_status',
            # 'planned_disbursement',
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

