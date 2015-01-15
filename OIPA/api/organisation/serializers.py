import iati
from rest_framework import serializers
from api.generics.serializers import DynamicFieldsModelSerializer
from api.fields import EncodedHyperlinkedIdentityField


class BasicOrganisationSerializer(DynamicFieldsModelSerializer):
    class NameSerializer(serializers.Serializer):
        def to_representation(self, obj):
            return {'narratives': [{'text': obj}, ], }

    class Meta:
        model = iati.models.Organisation
        fields = ('url', 'code', 'name')

    url = EncodedHyperlinkedIdentityField(view_name='organisation-detail')
    name = NameSerializer()


class OrganisationSerializer(BasicOrganisationSerializer):
    class TypeSerializer(serializers.ModelSerializer):
        class Meta:
            model = iati.models.OrganisationType
            fields = ('code',)

    type = TypeSerializer()
    reported_activities = EncodedHyperlinkedIdentityField(
        view_name='organisation-reported-activities')
    participated_activities = EncodedHyperlinkedIdentityField(
        view_name='organisation-participated-activities')
    
    provided_transactions = EncodedHyperlinkedIdentityField(
        view_name='organisation-provided-transactions')
    received_transactions = EncodedHyperlinkedIdentityField(
        view_name='organisation-received-transactions')

    class Meta:
        model = iati.models.Organisation
        fields = (
            'url',
            'code',
            'abbreviation',
            'type',
            'name',
            'original_ref',

            'reported_activities',
            'participated_activities',
            'provided_transactions',
            'received_transactions',
        )
