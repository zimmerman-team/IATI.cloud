from rest_framework import serializers

import iati
from api.generics.serializers import DynamicFieldsSerializer
from api.generics.serializers import DynamicFieldsModelSerializer
from api.generics.serializers import FilterableModelSerializer
from api.generics.fields import PointField
from api.sector.serializers import SectorSerializer
from api.region.serializers import RegionSerializer
from api.country.serializers import CountrySerializer
from api.activity.filters import BudgetFilter
from api.activity.filters import RelatedActivityFilter

# TODO: serialize vocabulary in codelist serializer
class VocabularySerializer(serializers.Serializer):
    code = serializers.CharField()
    name = serializers.CharField()

class CodelistSerializer(DynamicFieldsSerializer):
    code = serializers.CharField()
    name = serializers.CharField()

class CodelistCategorySerializer(CodelistSerializer):
    category = CodelistSerializer()

class CodelistVocabularySerializer(CodelistSerializer):
    vocabulary = VocabularySerializer()

# TODO: separate this
class NarrativeSerializer(serializers.ModelSerializer):
    text = serializers.CharField(source="content")
    language = CodelistSerializer()

    class Meta:
        model = iati.models.Narrative
        fields = (
            'text',
            'language',
        )

class NarrativeContainerSerializer(serializers.Serializer):
    narratives = NarrativeSerializer(many=True)


class DocumentCategorySerializer(serializers.ModelSerializer):

        class Meta:
            model = iati.models.DocumentCategory
            fields = ('code', 'name')


class DocumentLinkSerializer(serializers.ModelSerializer):

    format = CodelistSerializer(source='file_format')
    categories = DocumentCategorySerializer(many=True)
    title = NarrativeContainerSerializer(source="documentlinktitle_set", many=True)

    class Meta:
        model = iati.models.DocumentLink
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
        source='capital_spend',
        coerce_to_string=False
    )

    class Meta:
        model = iati.models.Activity
        fields = ('percentage',)


class BudgetSerializer(FilterableModelSerializer):

    class ValueSerializer(serializers.Serializer):
        currency = CodelistSerializer()
        date = serializers.CharField(source='value_date')
        value = serializers.DecimalField(
            max_digits=15,
            decimal_places=2,
            coerce_to_string=False,
        )

        class Meta:
            model = iati.models.Budget
            fields = (
                'value',
                'date',
                'currency',
            )

    value = ValueSerializer(source='*')
    type = CodelistSerializer()

    class Meta:
        model = iati.models.Budget
        filter_class = BudgetFilter
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
        model = iati.models.ActivityDate
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

    class Meta:
        model = iati.models.ActivityReportingOrganisation
        fields = (
            'ref',
            'type',
            'secondary_reporter',
            'narratives',
        )

class ParticipatingOrganisationSerializer(serializers.ModelSerializer):

    # TODO: Link to organisation standard (hyperlinked)
    ref = serializers.CharField(source='normalized_ref')
    type = CodelistSerializer()
    role = CodelistSerializer()
    narratives = NarrativeSerializer(many=True)

    class Meta:
        model = iati.models.ActivityParticipatingOrganisation
        fields = (
            'ref',
            'type',
            'role',
            'narratives',
        )

class ActivityPolicyMarkerSerializer(serializers.ModelSerializer):
    code = CodelistSerializer()
    vocabulary = VocabularySerializer()
    significance = CodelistSerializer()
    narratives = NarrativeSerializer(many=True)

    class Meta:
        model = iati.models.ActivityPolicyMarker
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
        model = iati.models.Title
        fields = ('narratives',)

class DescriptionSerializer(serializers.ModelSerializer):
    type = CodelistSerializer()
    narratives = NarrativeSerializer(many=True)

    class Meta:
        model = iati.models.Description
        fields = (
            'type',
            'narratives'
        )

class RelatedActivityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = iati.models.RelatedActivityType
        fields = (
            'code',
            'name'
        )

class RelatedActivitySerializer(FilterableModelSerializer):
    ref_activity = serializers.HyperlinkedRelatedField(view_name='activities:activity-detail', read_only=True)
    type = RelatedActivityTypeSerializer()

    class Meta:
        model = iati.models.RelatedActivity
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

    class Meta:
        model = iati.models.ActivitySector
        fields = (
            'sector',
            'percentage',
            'vocabulary',
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

    class Meta:
        model = iati.models.ActivityRecipientRegion
        fields = (
            'region',
            'percentage',
            'vocabulary',
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
        model = iati.models.ActivityRecipientCountry
        fields = (
            'country',
            'percentage',
        )


class ResultTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = iati.models.ResultType
        fields = (
            'code',
            'name',
        )

class ResultDescriptionSerializer(serializers.ModelSerializer):
    narratives = NarrativeSerializer(source="*")

    class Meta:
        model = iati.models.ResultDescription
        fields = (
            'narratives',
        )

class ResultTitleSerializer(serializers.ModelSerializer):
    narratives = NarrativeSerializer(source="*")

    class Meta:
        model = iati.models.ResultTitle
        fields = (
            'narratives',
        )

class ResultSerializer(serializers.ModelSerializer):

    type = CodelistSerializer() 
    title = NarrativeContainerSerializer(source="resulttitle_set")
    description = NarrativeContainerSerializer(source="resultdescription_set")
    # todo: add resultIndicator

    class Meta:
        model = iati.models.Result
        fields = (
            'title',
            'description',
            'result_type',
            'aggregation_status',
        )

class LocationSerializer(serializers.ModelSerializer):
    class LocationIdSerializer(serializers.Serializer):
        vocabulary = VocabularySerializer(
            source='location_id_vocabulary')
        code = serializers.CharField(source='location_id_code')

    class PointSerializer(serializers.Serializer):
        pos = PointField(source='point_pos')
        srs_name = serializers.CharField(source="point_srs_name")

    class AdministrativeSerializer(serializers.ModelSerializer):
        code = serializers.CharField()
        vocabulary = VocabularySerializer()

        class Meta:
            model = iati.models.LocationAdministrative
            fields = (
                'code',
                'vocabulary',
                'level',
            )

    location_reach = CodelistSerializer()
    location_id = LocationIdSerializer(source='*')
    name = NarrativeContainerSerializer(many=True, source="locationname_set")
    location_class = CodelistSerializer()
    description = NarrativeContainerSerializer(many=True, source="locationdescription_set")
    activity_description = NarrativeContainerSerializer(many=True, source="locationactivitydescription_set")
    feature_designation = CodelistCategorySerializer()
    administrative = AdministrativeSerializer(many=True, source="locationadministrative_set")
    exactness = CodelistSerializer()
    point = PointSerializer(source="*")

    class Meta:
        model = iati.models.Location
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

class ActivitySerializer(DynamicFieldsModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='activities:activity-detail')
    last_updated_datetime = serializers.DateTimeField(format="%y-%m-%d")
    activity_status = CodelistSerializer()
    activity_scope = CodelistSerializer(source='scope')
    capital_spend = CapitalSpendSerializer(source='*')
    collaboration_type = CodelistSerializer()
    default_aid_type = CodelistSerializer()
    default_currency = CodelistSerializer()
    default_finance_type = CodelistSerializer()
    default_flow_type = CodelistSerializer()
    default_tied_status = CodelistSerializer()
    activity_dates = ActivityDateSerializer(
        many=True,
        source='activitydate_set')
    reporting_organisations = ReportingOrganisationSerializer(
            many=True,)
    participating_organisations = ParticipatingOrganisationSerializer(
        many=True,)

    # transactions = TransactionSerializer(
    #     many=True,
    #     source='transaction_set'
    # )
    transactions = serializers.HyperlinkedIdentityField(
        view_name='activities:activity-transactions',
    )

    policy_markers = ActivityPolicyMarkerSerializer(
        many=True,
        source='activitypolicymarker_set'
    )
    recipient_countries = RecipientCountrySerializer(
        many=True,
        source='activityrecipientcountry_set'
    )
    sectors = ActivitySectorSerializer(
        many=True,
        source='activitysector_set'
    )
    recipient_regions = ActivityRecipientRegionSerializer(
        many=True,
        source='activityrecipientregion_set'
    )
    budgets = BudgetSerializer(many=True, source='budget_set')

    title = TitleSerializer()
    description = DescriptionSerializer(
        many=True, read_only=True, source='description_set')

    document_links = DocumentLinkSerializer(
        many=True,
        source='documentlink_set')
    results = ResultSerializer(many=True, source="result_set")
    locations = LocationSerializer(many=True, source='location_set')

    related_activities = RelatedActivitySerializer(many=True, source='relatedactivity_set')

    activity_aggregation = ActivityAggregationSerializer()
    child_aggregation = ActivityAggregationSerializer()
    activity_plus_child_aggregation = ActivityAggregationSerializer()

    class Meta:
        model = iati.models.Activity
        fields = (
            'url',
            'id',
            'iati_identifier',
            'title',
            'description',
            'last_updated_datetime',
            'default_currency',
            'hierarchy',
            'linked_data_uri',
            'reporting_organisations',
            'participating_organisations',
            'related_activities',
            'activity_status',
            'activity_dates',
            'activity_scope',
            'recipient_countries',
            'recipient_regions',
            'sectors',
            'transactions',
            'policy_markers',
            'collaboration_type',
            'default_flow_type',
            'default_finance_type',
            'default_aid_type',
            'default_tied_status',
            'budgets',
            'capital_spend',
            'xml_source_ref',
            'document_links',
            'results',
            'locations',
            'activity_aggregation',
            'child_aggregation',
            'activity_plus_child_aggregation'
        )


class CodelistSerializer(DynamicFieldsSerializer):
    code = serializers.CharField()
    name = serializers.CharField()