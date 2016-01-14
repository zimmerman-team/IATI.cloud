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

    transaction_type = CodelistSerializer()
    description = TransactionDescriptionSerializer()
    provider_org = TransactionProviderSerializer(source='provider_organisation')
    receiver_org = TransactionReceiverSerializer(source='receiver_organisation')
    flow_type = CodelistSerializer()
    finance_type = CodelistSerializer()
    aid_type = CodelistSerializer()
    tied_status = CodelistSerializer()
    currency = CodelistSerializer()

    class Meta:
        model = models.Transaction
        fields = (
            'url',
            'activity',
            'ref',
            'currency',
            'transaction_type',
            'transaction_date',
            'value',
            'value_date',
            'description',
            'provider_org',
            'receiver_org',
            'disbursement_channel',
            # 'sector',
            # 'recipient_country',
            # 'recipient_region',
            'flow_type',
            'finance_type',
            'aid_type',
            'tied_status',
        )

