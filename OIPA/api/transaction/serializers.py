from rest_framework import serializers
from iati.models import Transaction
from iati.models import TransactionType
from iati.models import Transaction
from iati.models import TransactionProvider
from iati.models import TransactionReceiver

from api.generics.serializers import DynamicFieldsModelSerializer
from api.organisation.serializers import BasicOrganisationSerializer
from api.activity.serializers import ActivitySerializer
from api.activity.serializers import AidTypeSerializer
from api.activity.serializers import CurrencySerializer
from api.activity.serializers import DescriptionTypeSerializer
from api.activity.serializers import FinanceTypeSerializer
from api.activity.serializers import FlowTypeSerializer
from api.activity.serializers import TiedStatusSerializer


class TransactionTypeSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = TransactionType
        fields = (
            'code',
            'name',
            'description',
        )


class TransactionProviderSerializer(serializers.ModelSerializer):

    organisation = BasicOrganisationSerializer()

    class Meta:
        model = TransactionProvider
        fields = ('organisation', 'name')


class TransactionReceiverSerializer(serializers.ModelSerializer):

    organisation = BasicOrganisationSerializer()

    class Meta:
        model = TransactionReceiver
        fields = ('organisation', 'name')


class TransactionSerializer(DynamicFieldsModelSerializer):
    """
    Transaction serializer class
    """
    url = serializers.HyperlinkedIdentityField(
        view_name='transactions:detail',
        lookup_field='pk')
    activity = ActivitySerializer(fields=('id', 'url'))
    aid_type = AidTypeSerializer
    description_type = DescriptionTypeSerializer()
    finance_type = FinanceTypeSerializer()
    flow_type = FlowTypeSerializer()
    provider_organisation = TransactionProviderSerializer()
    provider_activity = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='activities:activity-detail')
    receiver_organisation = TransactionReceiverSerializer()
    receiver_activity = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='activities:activity-detail')
    tied_status = TiedStatusSerializer()
    transaction_type = TransactionTypeSerializer(fields=('code', ))
    currency = CurrencySerializer()

    class Meta:
        model = Transaction
        fields = (
            'url',
            'activity',
            'aid_type',
            'description',
            'description_type',
            'disbursement_channel',
            'finance_type',
            'flow_type',
            'provider_organisation',
            'provider_activity',
            'receiver_organisation',
            'receiver_activity',
            'tied_status',
            'transaction_date',
            'transaction_type',
            'value_date',
            'value',
            'currency',
            'ref',
        )

