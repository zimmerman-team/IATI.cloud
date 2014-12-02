from rest_framework import serializers
import iati


class OrganisationDetailSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='organisation-detail')

    activity_reporting_organisation = serializers.RelatedField(
        many=True, read_only=True)
    activity_set = serializers.RelatedField(
        many=True, read_only=True)
    activityparticipatingorganisation_set = serializers.RelatedField(
        many=True, read_only=True)
    transaction_providing_organisation = serializers.RelatedField(
        many=True, read_only=True)
    transaction_receiving_organisation = serializers.RelatedField(
        many=True, read_only=True)

    class Meta:
        model = iati.models.Organisation
        fields = (
            'url',
            'code',
            'abbreviation',
            'type',
            'reported_by_organisation',
            'name',
            'original_ref',

            # Reverse linked data
            'activity_reporting_organisation',
            'activity_set',
            'activityparticipatingorganisation_set',
            'transaction_providing_organisation',
            'transaction_receiving_organisation',
        )

    def transform_url(self, obj, value):
        pass


class OrganisationListSerializer(OrganisationDetailSerializer):
    class Meta:
        model = iati.models.Organisation
