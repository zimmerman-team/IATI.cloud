from rest_framework import serializers

from iati.transaction import models

from api.generics.serializers import DynamicFieldsModelSerializer
from api.activity.serializers import ActivitySerializer, CodelistSerializer, NarrativeSerializer

class TransactionProviderSerializer(serializers.ModelSerializer):
    ref = serializers.CharField(source="normalized_ref")
    narratives = NarrativeSerializer(many=True)
    provider_activity = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='activities:activity-detail')
    provider_activity_id = serializers.CharField(source="provider_activity_ref")

    class Meta:
        model = models.TransactionProvider
        fields = (
            'ref',
            'provider_activity',
            'provider_activity_id',
            'narratives'
        )

class TransactionReceiverSerializer(serializers.ModelSerializer):
    ref = serializers.CharField(source="normalized_ref")
    narratives = NarrativeSerializer(many=True)
    receiver_activity = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='activities:activity-detail')
    receiver_activity_id = serializers.CharField(source="receiver_activity_ref")

    class Meta:
        model = models.TransactionReceiver
        fields = (
            'ref',
            'receiver_activity',
            'receiver_activity_id',
            'narratives'
        )

class TransactionDescriptionSerializer(serializers.ModelSerializer):
    narratives = NarrativeSerializer(many=True)

    class Meta:
        model = models.TransactionDescription
        fields = (
            'narratives',
        )

class TransactionSerializer(DynamicFieldsModelSerializer):
    """
    Transaction serializer class
    """
    url = serializers.HyperlinkedIdentityField(
        view_name='transactions:transaction-detail',
        lookup_field='pk')
    activity = ActivitySerializer(fields=('id', 'url'))
    aid_type = CodelistSerializer()
    finance_type = CodelistSerializer()
    flow_type = CodelistSerializer()
    provider_organisation = TransactionProviderSerializer()
    receiver_organisation = TransactionReceiverSerializer()
    tied_status = CodelistSerializer()
    transaction_type = CodelistSerializer()
    currency = CodelistSerializer()
    description = TransactionDescriptionSerializer()

    class Meta:
        model = models.Transaction
        fields = (
            'ref',
            'url',
            'activity',
            'aid_type',
            'description',
            'disbursement_channel',
            'finance_type',
            'flow_type',
            'provider_organisation',
            'receiver_organisation',
            'tied_status',
            'transaction_date',
            'transaction_type',
            'value_date',
            'value',
            'currency',
        )

