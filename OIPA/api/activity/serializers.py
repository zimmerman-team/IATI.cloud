from rest_framework import serializers
import iati


class ParticipatingOrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = iati.models.ActivityParticipatingOrganisation
        fields = (
            'activity',
            'organisation',
            'role',
            'name',
        )


class RecipientCountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = iati.models.ActivityRecipientCountry
        fields = (
            'activity',
            'country',
            'percentage',
        )


class ActivityDetailSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='activity-detail')

    # Linked fields
    sectors = serializers.HyperlinkedIdentityField(
        view_name='activity-sectors')
    participating_orgs = serializers.HyperlinkedIdentityField(
        view_name='activity-participating-organisations')

    # Reverse linked fields
    activitypolicymarker_set = serializers.RelatedField(many=True)
    activityrecipientcountry_set = serializers.HyperlinkedIdentityField(
        view_name='activity-recipient-countries')
    activityrecipientregion_set = serializers.RelatedField(many=True)
    activitysector_set = serializers.RelatedField(many=True)
    activitywebsite_set = serializers.RelatedField(many=True)
    budget_set = serializers.RelatedField(many=True)
    condition_set = serializers.RelatedField(many=True)
    contactinfo_set = serializers.RelatedField(many=True)
    countrybudgetitem_set = serializers.RelatedField(many=True)
    crsadd_set = serializers.RelatedField(many=True)
    current_activity = serializers.RelatedField(many=True)
    description_set = serializers.RelatedField(many=True)
    documentlink_set = serializers.RelatedField(many=True)
    ffs_set = serializers.RelatedField(many=True)
    location_set = serializers.RelatedField(many=True)
    otheridentifier_set = serializers.RelatedField(many=True)
    participating_organisations = serializers.RelatedField(many=True)
    planneddisbursement_set = serializers.RelatedField(many=True)
    result_set = serializers.RelatedField(many=True)
    title_set = serializers.RelatedField(many=True)
    transaction_set = serializers.RelatedField(many=True)

    class Meta:
        model = iati.models.Activity
        fields = (
            # Normal fields
            'url',
            'id',
            'iati_identifier',
            'default_currency',
            'hierarchy',
            'last_updated_datetime',
            'linked_data_uri',
            'reporting_organisation',  # iati: reporting_org
            'secondary_publisher',
            'activity_status',  # iati: activity-status
            'start_planned',
            'end_planned',
            'start_actual',
            'end_actual',
            'collaboration_type',
            'default_flow_type',
            'default_aid_type',
            'default_finance_type',
            'default_tied_status',
            'xml_source_ref',
            'total_budget_currency',
            'total_budget',
            'capital_spend',
            'scope',
            'iati_standard_version',

            # Linked fields
            'participating_organisation',
            'policy_marker',
            'sectors',
            'recipient_country',
            'recipient_region',

            # Reverse linked fields
            'activitypolicymarker_set',
            'activityrecipientcountry_set',
            'activityrecipientregion_set',
            'activitysector_set',
            'activitywebsite_set',
            'budget_set',
            'condition_set',
            'contactinfo_set',
            'countrybudgetitem_set',
            'crsadd_set',
            'current_activity',
            'description_set',  # iati: description || set name descriptions?
            'documentlink_set',
            'ffs_set',
            'location_set',
            'otheridentifier_set',  # iati: other-identifier || not a set
            'participating_orgs',
            'planneddisbursement_set',
            'result_set',
            'title_set',  # iati: title || use plural (titles) for set name?
            'transaction_set',
        )


class ActivityListSerializer(ActivityDetailSerializer):
    class Meta:
        model = iati.models.Activity
        fields = ('id', 'url', 'title_set')


class ActivitySectorSerializer(serializers.ModelSerializer):
    activity = serializers.HyperlinkedRelatedField(view_name='activity-detail')
    sector = serializers.HyperlinkedRelatedField(view_name='sector-detail')

    class Meta:
        model = iati.models.ActivitySector
        fields = (
            'activity',
            'sector',
            'alt_sector_name',
            'vocabulary',
            'percentage',
        )
