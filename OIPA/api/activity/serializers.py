from rest_framework import serializers
import iati
import geodata.models


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
    def to_representation(self, obj):
        return {
            'currency': getattr(obj.total_budget_currency, 'code', None),
            'value': obj.total_budget,
        }


class BudgetSerializer(serializers.ModelSerializer):

    class ValueSerializer(serializers.Serializer):
        def to_representation(self, obj):
            return {
                'value': obj.value,
                'date': obj.value_date,
                'currency': getattr(obj.currency, 'code', None),
            }

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
    def to_representation(self, obj):
        return {
            'code': getattr(obj.reporting_organisation, 'code', None),
            'name': getattr(obj.reporting_organisation, 'name', None),
            'secondary_publisher': obj.secondary_publisher
        }


class ActivityPolicyMarkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = iati.models.ActivityPolicyMarker
        fields = (
            'policy_marker',
            'alt_policy_marker',
            'activity',
            'vocabulary',
            'policy_significance',
        )


class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = iati.models.Title
        fields = (
            'title',
            'language',
        )


class DescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = iati.models.Description
        fields = (
            'description',
            'language',
        )


class ActivitySectorSerializer(serializers.ModelSerializer):
    sector = serializers.HyperlinkedRelatedField(
        queryset=iati.models.Sector.objects.all(),
        view_name='sector-detail')

    class Meta:
        model = iati.models.ActivitySector
        fields = (
            'sector',
            'percentage',
            'vocabulary',
        )


class ActivityRecipientRegionSerializer(serializers.ModelSerializer):
    region = serializers.HyperlinkedRelatedField(
        queryset=geodata.models.Region.objects.all(),
        view_name='region-detail')

    class Meta:
        model = iati.models.ActivityRecipientRegion
        fields = (
            'activity',
            'region',
            'percentage',
        )


class ParticipatingOrganisationSerializer(serializers.ModelSerializer):
    organisation = serializers.HyperlinkedRelatedField(
        queryset=iati.models.Organisation.objects.all(),
        view_name='organisation-detail')

    class Meta:
        model = iati.models.ActivityParticipatingOrganisation
        fields = (
            'organisation',
            'role',
            'name',
        )


class RecipientCountrySerializer(serializers.ModelSerializer):
    country = serializers.HyperlinkedRelatedField(
        queryset=geodata.models.Country.objects.all(),
        view_name='country-detail')

    class Meta:
        model = iati.models.ActivityRecipientCountry
        fields = (
            'country',
            'percentage',
        )


class ActivityDetailSerializer(serializers.ModelSerializer):
    activity_status = ActivityStatusSerializer()
    collaboration_type = CollaborationTypeSerializer()
    default_flow_type = DefaultFlowTypeSerializer()
    default_aid_type = DefaultAidTypeSerializer()
    url = serializers.HyperlinkedIdentityField(view_name='activity-detail')
    activity_dates = ActivityDateSerializer(source='*')
    total_budget = TotalBudgetSerializer(source='*')
    reporting_organisation = ReportingOrganisationSerializer(source='*')
    participating_organisations = ParticipatingOrganisationSerializer(
        many=True)

    activitypolicymarker_set = ActivityPolicyMarkerSerializer(many=True)
    activityrecipientcountry_set = RecipientCountrySerializer(many=True)
    activityrecipientregion_set = ActivityRecipientRegionSerializer(many=True)
    activitysector_set = ActivitySectorSerializer(many=True)
    budget_set = BudgetSerializer(many=True)
    description_set = DescriptionSerializer(many=True, read_only=True)
    title_set = TitleSerializer(many=True, read_only=True)

    class Meta:
        model = iati.models.Activity
        fields = (
            'url',
            'id',
            'iati_identifier',
            'total_budget',
            'capital_spend',
            'default_currency',
            'hierarchy',
            'last_updated_datetime',
            'linked_data_uri',
            'reporting_organisation',
            'activity_status',
            'activity_dates',
            'collaboration_type',
            'default_flow_type',
            'default_aid_type',
            'default_finance_type',
            'default_tied_status',
            'xml_source_ref',
            'scope',
            'iati_standard_version',

            'budget_set',
            'activitypolicymarker_set',
            'activityrecipientcountry_set',
            'activityrecipientregion_set',
            'activitysector_set',
            'description_set',
            'participating_organisations',
            'title_set',
        )


class ActivityListSerializer(ActivityDetailSerializer):
    class Meta:
        model = iati.models.Activity
