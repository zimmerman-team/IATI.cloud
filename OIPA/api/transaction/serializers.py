from rest_framework import serializers

from iati.transaction.models import Transaction
from iati_codelists.models import TransactionType

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
    provider_activity = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='activities:activity-detail')
    receiver_activity = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='activities:activity-detail')
    provider_organisation = BasicOrganisationSerializer()
    receiver_organisation = BasicOrganisationSerializer()
    tied_status = TiedStatusSerializer()
    transaction_type = TransactionTypeSerializer()
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

