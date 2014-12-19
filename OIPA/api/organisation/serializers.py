import iati
from rest_framework import serializers
from api.generics.serializers import DynamicFieldsModelSerializer


class OrganisationSerializer(DynamicFieldsModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='organisation-detail')

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
