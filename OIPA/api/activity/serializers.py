from rest_framework import serializers

import iati
from api.generics.serializers import DynamicFieldsModelSerializer, FilterableModelSerializer
from api.organisation.serializers import OrganisationSerializer
from api.sector.serializers import SectorSerializer
from api.region.serializers import RegionSerializer
# from api.region.serializers import RegionVocabularySerializer
from api.country.serializers import CountrySerializer
from api.fields import JSONField
from api.activity.filters import ActivityFilter, BudgetFilter, RelatedActivityFilter


class DocumentLinkSerializer(serializers.ModelSerializer):
    class FileFormatSerializer(serializers.ModelSerializer):
        class Meta:
            model = iati.models.FileFormat
            fields = ('code',)

    class DocumentCategorySerializer(serializers.ModelSerializer):
        class Meta:
            model = iati.models.DocumentCategory
            fields = ('code',)

    class TitleSerializer(serializers.Serializer):
        def to_representation(self, obj):
            return {'narratives': [{'text': obj.title}, ], }

    format = FileFormatSerializer(source='file_format')
    category = DocumentCategorySerializer(source='document_category')
    title = TitleSerializer(source='*')

    class Meta:
        model = iati.models.DocumentLink
        fields = (
            'url',
            'format',
            'category',
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


class TiedStatusSerializer(serializers.ModelSerializer):
    code = serializers.CharField()

    class Meta:
        model = iati.models.TiedStatus
        fields = ('code',)


class FinanceTypeSerializer(serializers.ModelSerializer):
    code = serializers.CharField()

    class Meta:
        model = iati.models.FinanceType
        fields = ('code',)


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = iati.models.Currency
        fields = ('code',)


class ActivityScopeSerializer(serializers.ModelSerializer):
    code = serializers.CharField()

    class Meta:
        model = iati.models.ActivityScope
        fields = ('code',)


class AidTypeSerializer(serializers.ModelSerializer):
    code = serializers.CharField()
    name = serializers.CharField()

    class Meta:
        model = iati.models.AidType
        fields = (
            'code', 'name'
        )


class FlowTypeSerializer(serializers.ModelSerializer):
    code = serializers.CharField()
    name = serializers.CharField()

    class Meta:
        model = iati.models.FlowType
        fields = (
            'code', 'name'
        )


class CollaborationTypeSerializer(serializers.ModelSerializer):
    code = serializers.CharField()
    name = serializers.CharField()

    class Meta:
        model = iati.models.CollaborationType
        fields = (
            'code', 'name'
        )


class ActivityStatusSerializer(serializers.ModelSerializer):
    code = serializers.CharField()
    name = serializers.CharField()

    class Meta:
        model = iati.models.ActivityStatus
        fields = (
            'code', 'name'
        )


class TotalBudgetSerializer(serializers.Serializer):
    currency = CurrencySerializer(source='total_budget_currency')
    value = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False,
        source='total_budget',
    )

    class Meta:
        model = iati.models.Activity
        fields = ('currency', 'value')

class BudgetSerializer(FilterableModelSerializer):
    class BudgetTypeSerializer(serializers.ModelSerializer):
        code = serializers.CharField()

        class Meta:
            model = iati.models.BudgetType
            fields = ('code',)

    class ValueSerializer(serializers.Serializer):
        currency = CurrencySerializer()
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
    type = BudgetTypeSerializer()

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
    def to_representation(self, obj):
        return {
            'start_planned': obj.start_planned,
            'end_planned': obj.end_planned,
            'start_actual': obj.start_actual,
            'end_actual': obj.end_actual
        }


class ReportingOrganisationSerializer(serializers.ModelSerializer):
    organisation = OrganisationSerializer(
        fields=('url', 'code', 'name', 'type'),
        source='reporting_organisation'
    )
    secondary_reporter = serializers.BooleanField(source='secondary_publisher')

    class Meta:
        model = iati.models.Activity
        fields = (
            'organisation',
            'secondary_reporter',
        )

class PolicyMarkerSerializer(serializers.ModelSerializer):
    code = serializers.CharField()

    class Meta:
        model = iati.models.PolicyMarker
        fields = ('code',)

class ActivityPolicyMarkerSerializer(serializers.ModelSerializer):


    class PolicySignificanceSerializer(serializers.ModelSerializer):
        code = serializers.CharField()

        class Meta:
            model = iati.models.PolicySignificance
            fields = ('code',)

    class VocabularySerializer(serializers.ModelSerializer):
        code = serializers.CharField()

        class Meta:
            model = iati.models.Vocabulary
            fields = ('code',)

    vocabulary = VocabularySerializer(serializers.ModelSerializer)
    code = PolicyMarkerSerializer(source='policy_marker')
    significance = PolicySignificanceSerializer(source='policy_significance')
    narative = serializers.CharField(source='alt_policy_marker')

    class Meta:
        model = iati.models.ActivityPolicyMarker
        fields = (
            'narative',
            'vocabulary',
            'significance',
            'code',
        )


class TitleSerializer(serializers.Serializer):
    class NarrativeSerializer(serializers.ModelSerializer):
        text = serializers.CharField(source='title')

        class Meta:
            model = iati.models.Title
            fields = ('text', 'language')

    narratives = NarrativeSerializer(many=True, source='title_set')


class DescriptionTypeSerializer(serializers.ModelSerializer):
    code = serializers.CharField()

    class Meta:
        model = iati.models.DescriptionType
        fields = ('code',)


class DescriptionSerializer(serializers.ModelSerializer):
    class NarrativeSerializer(serializers.ModelSerializer):
        text = serializers.CharField(source='description')

        def to_representation(self, obj):
            return [
                super(DescriptionSerializer.NarrativeSerializer, self)
                .to_representation(obj)
            ]

        class Meta:
            model = iati.models.Description
            fields = ('text', 'language')

    narratives = NarrativeSerializer(source='*')
    type = DescriptionTypeSerializer()

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
    current_activity = serializers.HyperlinkedRelatedField(view_name='activities:activity-detail', read_only=True)
    related_activity = serializers.HyperlinkedRelatedField(view_name='activities:activity-detail', read_only=True)
    type = RelatedActivityTypeSerializer()

    class Meta:
        model = iati.models.RelatedActivity
        filter_class = RelatedActivityFilter
        fields = (
            'current_activity',
            'related_activity',
            'ref',
            'type',
        )

class ActivitySectorSerializer(serializers.ModelSerializer):
    class VocabularySerializer(serializers.ModelSerializer):
        code = serializers.CharField()

        class Meta:
            model = iati.models.Vocabulary
            fields = ('code',)

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
    # vocabulary = RegionVocabularySerializer(source='region_vocabulary')
    region = RegionSerializer(
        fields=('url', 'code', 'name')
    )
    percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        coerce_to_string=False
    )

    class Meta:
        model = iati.models.ActivityRecipientRegion
        fields = (
            'region',
            'percentage',
            'vocabulary',
        )


class ParticipatingOrganisationSerializer(serializers.ModelSerializer):
    class OrganisationRoleSerializer(serializers.ModelSerializer):
        class Meta:
            model = iati.models.OrganisationRole
            fields = ('code',)

    role = OrganisationRoleSerializer()
    organisation = OrganisationSerializer(fields=('url', 'name', 'code'))

    class Meta:
        model = iati.models.ActivityParticipatingOrganisation
        fields = (
            'organisation',
            'role',
        )


class RecipientCountrySerializer(DynamicFieldsModelSerializer):
    country = CountrySerializer(fields=('url', 'code', 'name'))
    percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        coerce_to_string=False
    )

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


class NarrativeSerializer(serializers.Serializer):
        def to_representation(self, obj):
            return {'narratives': [{'text': obj}, ], }


class ResultSerializer(serializers.ModelSerializer):
    result_type = ResultTypeSerializer()
    title = NarrativeSerializer()
    description = NarrativeSerializer()

    class Meta:
        model = iati.models.Result
        fields = (
            'title',
            'description',
            'result_type',
            'aggregation_status',
        )

class GeographicVocabularySerializer(serializers.ModelSerializer):
    class Meta:
        model = iati.models.GeographicVocabulary
        fields = (
            'code',
        )


class LocationSerializer(serializers.ModelSerializer):
    class LocationIdSerializer(serializers.Serializer):
        vocabulary = GeographicVocabularySerializer(
            source='location_id_vocabulary')
        code = serializers.CharField(source='location_id_code')

    class AdministrativeSerializer(serializers.Serializer):
        vocabulary = GeographicVocabularySerializer(source='adm_vocabulary')
        level = serializers.IntegerField(source='adm_level')
        code = serializers.CharField(source='adm_code')

    class GeographicLocationClassSerializer(serializers.ModelSerializer):
        class Meta:
            model = iati.models.GeographicLocationClass
            fields = (
                'code',
            )

    class GeographicLocationReachSerializer(serializers.ModelSerializer):
        class Meta:
            model = iati.models.GeographicLocationReach
            fields = (
                'code',
            )

    class GeographicExactnessSerializer(serializers.ModelSerializer):
        class Meta:
            model = iati.models.GeographicExactness
            fields = (
                'code',
            )

    class LocationTypeSerializer(serializers.ModelSerializer):
        class LocationTypeCategorySerializer(serializers.ModelSerializer):
            class Meta:
                model = iati.models.LocationTypeCategory
                fields = (
                    'code',
                )
        category = LocationTypeCategorySerializer

        class Meta:
            model = iati.models.LocationType
            fields = (
                'code',
                'category',
            )

    location_reach = GeographicLocationReachSerializer()
    location_id = LocationIdSerializer(source='*')
    name = NarrativeSerializer()
    description = NarrativeSerializer()
    activity_description = NarrativeSerializer()
    administrative = AdministrativeSerializer(source='*')
    point = JSONField(source='point.json')
    exactness = GeographicExactnessSerializer()
    location_class = GeographicLocationClassSerializer()
    feature_designation = LocationTypeSerializer()

    class Meta:
        model = iati.models.Location
        fields = (
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
    activity_status = ActivityStatusSerializer()
    activity_scope = ActivityScopeSerializer(source='scope')
    capital_spend = CapitalSpendSerializer(source='*')
    collaboration_type = CollaborationTypeSerializer()
    default_aid_type = AidTypeSerializer()
    default_currency = CurrencySerializer()
    default_finance_type = FinanceTypeSerializer()
    default_flow_type = FlowTypeSerializer()
    default_tied_status = TiedStatusSerializer()
    activity_dates = ActivityDateSerializer(source='*')
    total_budget = TotalBudgetSerializer(source='*')
    reporting_organisation = ReportingOrganisationSerializer(source='*')
    participating_organisations = ParticipatingOrganisationSerializer(
        many=True)
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
    descriptions = DescriptionSerializer(
        many=True, read_only=True, source='description_set')
    title = TitleSerializer(source='*')
    document_links = DocumentLinkSerializer(
        many=True,
        source='documentlink_set')
    results = ResultSerializer(many=True)
    locations = LocationSerializer(many=True, source='location_set')

    related_activities = RelatedActivitySerializer(many=True, source='current_activity')

    class Meta:
        model = iati.models.Activity
        fields = (
            'url',
            'id',
            'iati_identifier',
            'last_updated_datetime',
            'default_currency',
            'hierarchy',
            'linked_data_uri',
            'reporting_organisation',
            'title',
            'descriptions',
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
            'total_budget',
            'xml_source_ref',
            'document_links',
            'results',
            'locations'
        )
        