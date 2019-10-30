from rest_framework import serializers

import api.sector.serializers
import api.transaction.serializers
from api.codelist.serializers import (
    CodelistSerializer, NarrativeSerializer
)
from api.country.serializers import CountrySerializer
from api.region.serializers import BasicRegionSerializer
from iati.transaction import models


class TransactionProviderSerializer(serializers.ModelSerializer):
    ref = serializers.CharField()
    type = CodelistSerializer()
    narratives = NarrativeSerializer(many=True)
    provider_activity_id = serializers.CharField(
        source="provider_activity_ref", required=False)

    class Meta:
        model = models.TransactionProvider
        fields = (
            'ref',
            'type',
            'provider_activity_id',
            'narratives'
        )


class TransactionReceiverSerializer(serializers.ModelSerializer):
    ref = serializers.CharField()
    type = CodelistSerializer()
    narratives = NarrativeSerializer(many=True)
    receiver_activity_id = serializers.CharField(
        source="receiver_activity_ref"
    )

    class Meta:
        model = models.TransactionReceiver
        fields = (
            'ref',
            'type',
            'receiver_activity',
            'receiver_activity_id',
            'narratives'
        )


class TransactionRecipientCountrySerializer(api.transaction.serializers.TransactionRecipientCountrySerializer):
    country = CountrySerializer(fields=('code', 'name'))


class TransactionRecipientRegionSerializer(api.transaction.serializers.TransactionRecipientRegionSerializer):
    region = BasicRegionSerializer(
        fields=('code', 'name'),
    )


class TransactionSectorSerializer(api.transaction.serializers.TransactionSectorSerializer):
    sector = api.sector.serializers.SectorSerializer(fields=('code', 'name'))


class TransactionSerializer(api.transaction.serializers.TransactionSerializer):
    sector = TransactionSectorSerializer(
        required=False, source="transaction_sector"
    )
    sectors = TransactionSectorSerializer(
        many=True, read_only=True, required=False, source="transactionsector_set")
    recipient_countries = TransactionRecipientCountrySerializer(
        many=True, read_only=True, required=False, source="transactionrecipientcountry_set")  # NOQA: E501

    recipient_regions = TransactionRecipientRegionSerializer(
        many=True, read_only=True, required=False, source="transactionrecipientregion_set")  # NOQA: E501

    recipient_country = TransactionRecipientCountrySerializer(
        required=False, source="transaction_recipient_country")
    recipient_region = TransactionRecipientRegionSerializer(
        required=False, source="transaction_recipient_region")

    provider_organisation = TransactionProviderSerializer(required=False)
    receiver_organisation = TransactionReceiverSerializer(required=False)
