from django.conf import settings
from rest_framework import serializers
from iati.currency_converter import convert
from iati.models import Transaction
from iati.models import TransactionType

from api.generics.serializers import DynamicFieldsModelSerializer
from api.organisation.serializers import OrganisationSerializer
from api.activity.serializers import ActivitySerializer
from api.activity.serializers import AidTypeSerializer
from api.activity.serializers import CurrencySerializer
from api.activity.serializers import DescriptionTypeSerializer
from api.activity.serializers import FinanceTypeSerializer
from api.activity.serializers import FlowTypeSerializer
from api.activity.serializers import TiedStatusSerializer


class OriginalValueSerializer(serializers.Serializer):
    currency = CurrencySerializer()
    date = serializers.CharField(source='value_date')
    value = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        coerce_to_string=True,
    )

    class Meta:
        model = Transaction
        fields = (
            'value',
            'date',
            'currency',
        )


class ValueSerializer(serializers.Serializer):
    currency = serializers.SerializerMethodField()
    date = serializers.CharField(source='value_date')
    converted_value = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = (
            'converted_value',
            'date',
            'currency',
        )
        default_currency = settings.API_SETTINGS['DEFAULT_CURRENCY']
        currency_param = settings.API_SETTINGS['CURRENCY_PARAM']

    def get_currency(self, obj):
        return {'code': self.get_request_currency(), }

    def get_converted_value(self, obj):
        return convert.to_currency(
            self.get_request_currency(),
            obj.value_date, obj.xdr_value)

    def get_request_currency(self):
        request = self.context['request']
        currency = request.GET.get(
            self.Meta.currency_param,
            self.Meta.default_currency
        )
        return currency


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
    provider_organisation = OrganisationSerializer()
    receiver_organisation = OrganisationSerializer()
    tied_status = TiedStatusSerializer()
    transaction_type = TransactionTypeSerializer(fields=('code', ))
    original_value = OriginalValueSerializer(source='*')
    value = ValueSerializer(source='*')

    class Meta:
        model = Transaction
        fields = (
            'value',
            'original_value',
            'id',
            'url',
            'activity',
            'aid_type',
            'description',
            'description_type',
            'disbursement_channel',
            'finance_type',
            'flow_type',
            'provider_organisation',
            'provider_organisation_name',
            'provider_activity',
            'receiver_organisation',
            'receiver_organisation_name',
            'tied_status',
            'transaction_date',
            'transaction_type',
            'ref',
        )
