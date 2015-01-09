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
    reported_activities = serializers.HyperlinkedIdentityField(
        source='activity_reporting_organisation',
        view_name='organisation-reported-activities')
    participated_activities = serializers.HyperlinkedIdentityField(
        source='activity_participating_organisation',
        view_name='organisation-participated-activities')

    # These fields will need to be replaced once the TransactionSerializer
    # is done
    provided_transactions = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=iati.models.Transaction.objects.all(),
        source='transaction_providing_organisation')
    received_transactions = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=iati.models.Transaction.objects.all(),
        source='transaction_receiving_organisation')

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
