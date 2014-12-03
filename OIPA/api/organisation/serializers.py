from rest_framework import serializers
import iati


class OrganisationDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = iati.models.Organisation
        fields = (
            'code',
            'abbreviation',
            'type',
            'reported_by_organisation',
            'name',
            'original_ref',

            # Reverse linked data
            # 'activity_reporting_organisation',
            # 'activity_set',
            # 'activityparticipatingorganisation_set',
            # 'transaction_providing_organisation',
            # 'transaction_receiving_organisation',
        )


class OrganisationListSerializer(OrganisationDetailSerializer):
    class Meta:
        model = iati.models.Organisation
