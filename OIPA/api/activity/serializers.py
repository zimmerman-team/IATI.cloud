from rest_framework import serializers
import iati
from api.fields import RootField


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = iati.models.Transaction
        fields = ()

    def transform_id(self, obj, value):
        pass
    # id
    # activity
    # aid_type
    # currency
    # description
    # description_type
    # disbursement_channel
    # finance_type
    # flow_type
    # provider_organisation
    # provider_organisation_name
    # receiver_organisation
    # tied_status
    # transaction_date
    # transaction_type
    # value_date
    # value
    # currency
    # ref


class AidTypeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = iati.models.AidTypeCategory
        fields = ()


class DefaultAidTypeSerializer(serializers.ModelSerializer):
    category = AidTypeCategorySerializer()

    class Meta:
        model = iati.models.AidType
        fields = (
            'code',
            'name',
            'description',
            'category',
        )


class DefaultFlowTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = iati.models.FlowType
        fields = (
            'code',
            'name',
            'description',
        )


class CollaborationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = iati.models.CollaborationType
        fields = (
            'code',
            'name',
            'description',
        )


class ActivityStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = iati.models.ActivityStatus
        fields = ()


class TotalBudgetSerializer(serializers.Serializer):
    currency = serializers.Field(source='total_budget_currency')
    value = serializers.Field(source='total_budget')


class BudgetSerializer(serializers.ModelSerializer):
    class ValueSerializer(serializers.Serializer):
        value = serializers.Field()
        date = serializers.Field(source='value_date')
        currencty = serializers.Field(source='currency')

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
    start_planned = RootField()
    end_planned = RootField()
    start_actual = RootField()
    end_actual = RootField()


class ReportingOrganisationSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    secondary_publisher = RootField()

    class Meta:
        model = iati.models.Organisation
        fields = (
            'code',
            'name',
            'secondary_publisher',
        )


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
    activity = serializers.HyperlinkedRelatedField(view_name='activity-detail')
    activity_id = serializers.Field(source='activity.id')
    sector = serializers.HyperlinkedRelatedField(
        view_name='sector-detail')
    sector_code = serializers.Field(source='sector.code')

    class Meta:
        model = iati.models.ActivitySector
        fields = (
            'activity_id',
            'activity',
            'sector_code',
            'sector',
            'percentage',
            'vocabulary',
        )


class ActivityRecipientRegionSerializer(serializers.ModelSerializer):
    activity = serializers.HyperlinkedRelatedField(view_name='activity-detail')
    activity_id = serializers.Field(source='activity.id')
    region = serializers.HyperlinkedRelatedField(
        view_name='region-detail')
    region_code = serializers.Field(source='region.code')

    class Meta:
        model = iati.models.ActivityRecipientRegion
        fields = (
            'activity_id',
            'activity',
            'region_code',
            'region',
            'percentage',
        )


class ParticipatingOrganisationSerializer(serializers.ModelSerializer):
    activity = serializers.HyperlinkedRelatedField(view_name='activity-detail')
    activity_id = serializers.Field(source='activity.id')
    organisation = serializers.HyperlinkedRelatedField(
        view_name='organisation-detail')
    organisation_id = serializers.Field(source='organisation.code')

    class Meta:
        model = iati.models.ActivityParticipatingOrganisation
        fields = (
            'activity_id',
            'activity',
            'organisation_id',
            'organisation',
            'role',
            'name',
        )


class RecipientCountrySerializer(serializers.ModelSerializer):
    activity = serializers.HyperlinkedRelatedField(view_name='activity-detail')
    activity_id = serializers.Field(source='activity.id')
    country = serializers.HyperlinkedRelatedField(view_name='country-detail')
    country_id = serializers.Field(source='country.code')

    class Meta:
        model = iati.models.ActivityRecipientCountry
        fields = (
            'activity_id',
            'activity',
            'country_id',
            'country',
            'percentage',
        )


class ActivityDetailSerializer(serializers.ModelSerializer):
    activity_status = ActivityStatusSerializer()
    collaboration_type = CollaborationTypeSerializer()
    default_flow_type = DefaultFlowTypeSerializer()
    default_aid_type = DefaultAidTypeSerializer()

    url = serializers.HyperlinkedIdentityField(view_name='activity-detail')
    activity_dates = ActivityDateSerializer(source='start_planned')
    total_budget = TotalBudgetSerializer(source='*')
    reporting_organisation = ReportingOrganisationSerializer()
    # Linked fields
    participating_organisations = ParticipatingOrganisationSerializer()

    # Reverse linked fields
    activitypolicymarker_set = ActivityPolicyMarkerSerializer(many=True)
    activityrecipientcountry_set = RecipientCountrySerializer()
    activityrecipientregion_set = ActivityRecipientRegionSerializer(many=True)
    activitysector_set = ActivitySectorSerializer(many=True)
    activitywebsite_set = serializers.RelatedField(many=True)
    budget_set = BudgetSerializer(many=True)
    condition_set = serializers.RelatedField(many=True)
    contactinfo_set = serializers.RelatedField(many=True)
    countrybudgetitem_set = serializers.RelatedField(many=True)
    crsadd_set = serializers.RelatedField(many=True)
    current_activity = serializers.RelatedField(many=True)
    description_set = DescriptionSerializer(many=True)
    documentlink_set = serializers.RelatedField(many=True)
    ffs_set = serializers.RelatedField(many=True)
    location_set = serializers.RelatedField(many=True)
    otheridentifier_set = serializers.RelatedField(many=True)
    planneddisbursement_set = serializers.RelatedField(many=True)
    result_set = serializers.RelatedField(many=True)
    title_set = TitleSerializer(many=True)
    transaction_set = TransactionSerializer(many=True)

    class Meta:
        model = iati.models.Activity
        fields = (
            # Normal fields
            'url',
            'id',
            'iati_identifier',
            'budget_set',
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

            # Reverse linked fields
            'activitypolicymarker_set',
            'activityrecipientcountry_set',
            'activityrecipientregion_set',
            'activitysector_set',
            'activitywebsite_set',
            'condition_set',
            'contactinfo_set',
            'countrybudgetitem_set',
            'crsadd_set',
            'current_activity',
            'description_set',
            'documentlink_set',
            'ffs_set',
            'location_set',
            'otheridentifier_set',
            'participating_organisations',
            'planneddisbursement_set',
            'result_set',
            'title_set',
            'transaction_set',
        )


class ActivityListSerializer(ActivityDetailSerializer):
    def __init__(self, *args, **kwargs):
        # Instantiate the superclass normally
        super(ActivityListSerializer, self).__init__(*args, **kwargs)

        fields = ['id', 'url', 'title_set']
        fields_param = self.context['request'].QUERY_PARAMS.get('fields', None)

        if fields_param is not None:
            fields.extend(fields_param.split(','))
        
        keep_fields = set(fields)
        all_fields = set(self.fields.keys())
        for field_name in all_fields - keep_fields:
            self.fields.pop(field_name)

    class Meta:
        model = iati.models.Activity
        
    

class ActivitySectorSerializer(serializers.ModelSerializer):
    activity_id = serializers.Field(source='activity.id')
    activity = serializers.HyperlinkedRelatedField(view_name='activity-detail')
    sector_id = serializers.Field(source='sector.code')
    sector = serializers.HyperlinkedRelatedField(view_name='sector-detail')

    class Meta:
        model = iati.models.ActivitySector
        fields = (
            'activity_id',
            'activity',
            'sector_id',
            'sector',
            'alt_sector_name',
            'vocabulary',
            'percentage',
        )
