from rest_framework import serializers
import iati
from api.serializers import DynamicFieldsModelSerializer
from api.organisation.serializers import OrganisationSerializer
from api.sector.serializers import SectorSerializer
from api.region.serializers import RegionSerializer
from api.country.serializers import CountrySerializer


class CapitalSpendSerializer(serializers.ModelSerializer):
    percentage = serializers.DecimalField(
        max_digits=5, decimal_places=2, source='capital_spend')

    class Meta:
        model = iati.models.Activity
        fields = ('percentage',)


class TiedStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = iati.models.TiedStatus
        fields = ('code',)


class FinanceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = iati.models.FinanceType
        fields = ('code',)


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = iati.models.Currency
        fields = ('code',)


class ActivityScopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = iati.models.ActivityScope
        fields = ('code',)


class DefaultAidTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = iati.models.AidType
        fields = (
            'code',
        )


class DefaultFlowTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = iati.models.FlowType
        fields = (
            'code',
        )


class CollaborationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = iati.models.CollaborationType
        fields = (
            'code',
        )


class ActivityStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = iati.models.ActivityStatus
        fields = (
            'code',
        )


class TotalBudgetSerializer(serializers.Serializer):
    currency = CurrencySerializer(source='total_budget_currency')
    value = serializers.CharField(source='total_budget')

    class Meta:
        model = iati.models.Activity
        fields = ('currency', 'value')


class BudgetSerializer(serializers.ModelSerializer):

    class ValueSerializer(serializers.Serializer):
        currency = CurrencySerializer()
        date = serializers.CharField(source='value_date')
        value = serializers.CharField()

        class Meta:
            model = iati.models.Budget
            fields = (
                'value',
                'date',
                'currency',
            )

    value = ValueSerializer(source='*')

    class Meta:
        model = iati.models.Budget
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


class ActivityPolicyMarkerSerializer(serializers.ModelSerializer):
    class PolicyMarkerSerializer(serializers.ModelSerializer):
        class Meta:
            model = iati.models.PolicyMarker
            fields = ('code',)

    class PolicySignificanceSerializer(serializers.ModelSerializer):
        class Meta:
            model = iati.models.PolicySignificance
            fields = ('code',)

    class VocabularySerializer(serializers.ModelSerializer):
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


class DescriptionSerializer(serializers.ModelSerializer):
    class NarrativeSerializer(serializers.ModelSerializer):
        text = serializers.CharField(source='description')

        class Meta:
            model = iati.models.Description
            fields = ('text', 'language')

    narratives = NarrativeSerializer(source='*')

    class Meta:
        model = iati.models.Description
        fields = (
            'type',
            'rsr_description_type_id',
            'narratives'
        )


class ActivitySectorSerializer(serializers.ModelSerializer):
    class VocabularySerializer(serializers.ModelSerializer):
        class Meta:
            model = iati.models.Vocabulary
            fields = ('code',)

    sector = SectorSerializer(fields=('url', 'code', 'name'))
    vocabulary = VocabularySerializer()

    class Meta:
        model = iati.models.ActivitySector
        fields = (
            'sector',
            'percentage',
            'vocabulary',
        )


class ActivityRecipientRegionSerializer(serializers.ModelSerializer):
    class RegionVocabularySerializer(serializers.ModelSerializer):
        class Meta:
            model = iati.models.RegionVocabulary
            fields = ('code',)

    vocabulary = RegionVocabularySerializer(source='region_vocabulary')
    region = RegionSerializer(
        fields=('url', 'code', 'name')
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


class RecipientCountrySerializer(serializers.ModelSerializer):
    country = CountrySerializer(fields=('url', 'code', 'name'))

    class Meta:
        model = iati.models.ActivityRecipientCountry
        fields = (
            'country',
            'percentage',
        )


class ActivitySerializer(DynamicFieldsModelSerializer):
    activity_status = ActivityStatusSerializer()
    activity_scope = ActivityScopeSerializer(source='scope')
    capital_spend = CapitalSpendSerializer(source='*')
    collaboration_type = CollaborationTypeSerializer()
    default_aid_type = DefaultAidTypeSerializer()
    default_currency = CurrencySerializer()
    default_finance_type = FinanceTypeSerializer()
    default_flow_type = DefaultFlowTypeSerializer()
    default_tied_status = TiedStatusSerializer()
    url = serializers.HyperlinkedIdentityField(view_name='activity-detail')
    activity_dates = ActivityDateSerializer(source='*')
    total_budget = TotalBudgetSerializer(source='*')
    reporting_organisation = ReportingOrganisationSerializer(source='*')
    participating_organisations = ParticipatingOrganisationSerializer(
        many=True)

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
            'activity_status',
            'activity_dates',
            'activity_scope',
            'recipient_countries',
            'recipient_regions',
            'sectors',
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
        )
