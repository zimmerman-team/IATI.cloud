from rest_framework import serializers

from api.activity.serializers import (
    ActivitySerializer, handle_errors, save_narratives
)
from api.codelist.serializers import (
    CodelistSerializer, NarrativeSerializer, VocabularySerializer
)
from api.country.serializers import CountrySerializer
from api.generics.serializers import DynamicFieldsModelSerializer
from api.generics.utils import get_or_raise
from api.region.serializers import BasicRegionSerializer
from api.sector.serializers import SectorSerializer
from iati import models as iati_models
from iati.parser import validators
from iati.transaction import models


class TransactionProviderSerializer(serializers.ModelSerializer):
    ref = serializers.CharField()
    type = CodelistSerializer()
    narratives = NarrativeSerializer(many=True)
    provider_activity = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='activities:activity-detail')
    provider_activity_id = serializers.CharField(
        source="provider_activity_ref", required=False)

    class Meta:
        model = models.TransactionProvider
        fields = (
            'ref',
            'type',
            'provider_activity',
            'provider_activity_id',
            'narratives'
        )


class TransactionReceiverSerializer(serializers.ModelSerializer):
    ref = serializers.CharField()
    type = CodelistSerializer()
    narratives = NarrativeSerializer(many=True)
    receiver_activity = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='activities:activity-detail')
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


class TransactionDescriptionSerializer(serializers.ModelSerializer):
    narratives = NarrativeSerializer(many=True)

    class Meta:
        model = models.TransactionDescription
        fields = (
            'narratives',
        )


class TransactionSectorSerializer(serializers.ModelSerializer):
    sector = SectorSerializer(fields=('url', 'code', 'name'))
    vocabulary = VocabularySerializer()
    vocabulary_uri = serializers.URLField()

    class Meta:
        model = models.TransactionSector
        fields = (
            'id',
            'sector',
            'vocabulary',
            'vocabulary_uri',
        )


class TransactionRecipientCountrySerializer(DynamicFieldsModelSerializer):
    country = CountrySerializer(fields=('url', 'code', 'name'))

    class Meta:
        model = models.TransactionRecipientCountry
        fields = (
            'id',
            'country',
        )


class TransactionRecipientRegionSerializer(DynamicFieldsModelSerializer):
    region = BasicRegionSerializer(
        fields=('url', 'code', 'name'),
    )
    vocabulary = VocabularySerializer()
    vocabulary_uri = serializers.URLField(required=False)

    class Meta:
        model = models.TransactionRecipientRegion
        fields = (
            'id',
            'region',
            'vocabulary',
            'vocabulary_uri',
        )


class TransactionSerializer(DynamicFieldsModelSerializer):
    """
    Transaction serializer class
    """
    url = serializers.HyperlinkedIdentityField(
        view_name='transactions:transaction-detail',
        lookup_field='pk',
        read_only=True
    )

    transaction_date = serializers.CharField()
    value_date = serializers.CharField()
    aid_type = CodelistSerializer()
    disbursement_channel = CodelistSerializer()
    finance_type = CodelistSerializer()
    flow_type = CodelistSerializer()
    provider_organisation = TransactionProviderSerializer(required=False)
    receiver_organisation = TransactionReceiverSerializer(required=False)
    disbursement_channel = CodelistSerializer()
    sector = TransactionSectorSerializer(
        required=False, source="transaction_sector")

    sectors = TransactionSectorSerializer(
        many=True, read_only=True, required=False, source="transactionsector_set")  # NOQA: E501

    recipient_countries = TransactionRecipientCountrySerializer(
        many=True, read_only=True, required=False, source="transactionrecipientcountry_set")  # NOQA: E501

    recipient_regions = TransactionRecipientRegionSerializer(
        many=True, read_only=True, required=False, source="transactionrecipientregion_set") # NOQA: E501

    recipient_country = TransactionRecipientCountrySerializer(
        required=False, source="transaction_recipient_country")
    recipient_region = TransactionRecipientRegionSerializer(
        required=False, source="transaction_recipient_region")
    tied_status = CodelistSerializer()
    transaction_type = CodelistSerializer()
    currency = CodelistSerializer()
    description = TransactionDescriptionSerializer()
    humanitarian = serializers.BooleanField()

    activity = ActivitySerializer(read_only=True, fields=(
        'id', 'iati_identifier', 'url', 'title'))
    activity_id = serializers.CharField(write_only=True)

    iati_identifier = serializers.CharField(source='activity.iati_identifier', required=False)  # NOQA: E501

    class Meta:
        model = models.Transaction
        fields = (
            'id',
            'activity',
            'activity_id',
            'url',
            'ref',
            'humanitarian',
            'transaction_type',
            'transaction_date',
            'value',
            'value_date',
            'currency',
            'description',
            'provider_organisation',
            'receiver_organisation',
            'disbursement_channel',
            'sector',
            'recipient_country',
            'recipient_region',
            'flow_type',
            'finance_type',
            'aid_type',
            'tied_status',
            'sectors',
            'iati_identifier',
            'recipient_countries',
            'recipient_regions'

        )

    def validate(self, data):

        activity = get_or_raise(iati_models.Activity, data, 'activity_id')

        validated = validators.activity_transaction(
            activity,
            data.get('ref'),
            data.get('humanitarian'),
            data.get('transaction_type', {}).get('code'),
            data.get('transaction_date'),
            data.get('value'),
            data.get('value_date'),
            data.get('currency', {}).get('code'),
            data.get('description', {}).get('narratives'),
            data.get('provider_organisation', {}).get('ref'),
            data.get('provider_organisation', {}).get('provider_activity_ref'),
            data.get('provider_organisation', {}).get('type', {}).get('code'),
            data.get('provider_organisation', {}).get('narratives'),
            data.get('receiver_organisation', {}).get('ref'),
            data.get('receiver_organisation', {}).get('receiver_activity_ref'),
            data.get('receiver_organisation', {}).get('type', {}).get('code'),
            data.get('receiver_organisation', {}).get('narratives'),
            data.get('disbursement_channel', {}).get('code'),
            data.get('transaction_sector', {}).get(
                'sector', {}).get('code', {}),
            data.get('transaction_sector', {}).get(
                'vocabulary', {}).get('code', {}),
            data.get('transaction_sector', {}).get('vocabulary_uri', {}),
            data.get('transaction_recipient_country', {}).get(
                'country', {}).get('code', {}),
            data.get('transaction_recipient_region', {}).get(
                'region', {}).get('code', {}),
            data.get('transaction_recipient_region', {}).get(
                'vocabulary', {}).get('code', {}),
            data.get('transaction_recipient_region', {}).get('vocabulary_uri'),
            data.get('flow_type', {}).get('code'),
            data.get('finance_type', {}).get('code'),
            data.get('aid_type', {}).get('code'),
            data.get('tied_status', {}).get('code'),
        )

        return handle_errors(validated)

    def create(self, validated_data):
        activity = validated_data.get('activity')
        description_narratives_data = validated_data.pop(  # NOQA: F841
            'description_narratives', [])
        provider_data = validated_data.pop('provider_org')
        provider_narratives_data = validated_data.pop(
            'provider_org_narratives', [])
        receiver_data = validated_data.pop('receiver_org')
        receiver_narratives_data = validated_data.pop(
            'receiver_org_narratives', [])
        sector_data = validated_data.pop('sector')
        recipient_country_data = validated_data.pop('recipient_country')
        recipient_region_data = validated_data.pop('recipient_region')

        instance = models.Transaction.objects.create(**validated_data)

        if provider_data.get('ref'):
            provider_org = models.TransactionProvider.objects.create(
                transaction=instance,
                **provider_data)
            save_narratives(provider_org, provider_narratives_data, activity)
            validated_data['provider_organisation'] = provider_org

        if receiver_data.get('ref'):
            receiver_org = models.TransactionReceiver.objects.create(
                transaction=instance,
                **receiver_data)
            save_narratives(receiver_org, receiver_narratives_data, activity)
            validated_data['receiver_organisation'] = receiver_org

        if sector_data.get('sector'):
            models.TransactionSector.objects.create(
                transaction=instance,
                reported_transaction=instance,
                percentage=100,
                **sector_data
            )

        if recipient_country_data.get('country'):
            models.TransactionRecipientCountry.objects.create(
                transaction=instance,
                reported_transaction=instance,
                percentage=100,
                **recipient_country_data
            )

        if recipient_region_data.get('region'):
            models.TransactionRecipientRegion.objects.create(
                transaction=instance,
                reported_transaction=instance,
                percentage=100,
                **recipient_region_data
            )

        return instance

    def update(self, instance, validated_data):
        activity = validated_data.get('activity')
        description_narratives_data = validated_data.pop(  # NOQA: F841
            'description_narratives', [])
        provider_data = validated_data.pop('provider_org')
        provider_narratives_data = validated_data.pop(
            'provider_org_narratives', [])
        receiver_data = validated_data.pop('receiver_org')
        receiver_narratives_data = validated_data.pop(
            'receiver_org_narratives', [])
        sector_data = validated_data.pop('sector')
        recipient_country_data = validated_data.pop('recipient_country')
        recipient_region_data = validated_data.pop('recipient_region')

        update_instance = models.Transaction(**validated_data)
        update_instance.id = instance.id
        update_instance.save()

        if provider_data.get('ref'):
            try:
                provider_org = models.TransactionProvider.objects.get(
                    transaction=instance)
            except BaseException:
                provider_org = models.TransactionProvider.objects.create(
                    transaction=instance,
                    **provider_data)
            save_narratives(provider_org, provider_narratives_data, activity)
            validated_data['provider_organisation'] = provider_org

        if receiver_data.get('ref'):
            try:
                receiver_org = models.TransactionReceiver.objects.get(
                    transaction=instance)
            except BaseException:
                receiver_org = models.TransactionReceiver.objects.create(
                    transaction=instance,
                    **receiver_data)
            save_narratives(receiver_org, receiver_narratives_data, activity)
            validated_data['receiver_organisation'] = receiver_org

        if sector_data.get('sector'):
            try:
                models.TransactionSector.objects.get(
                    transaction=instance,
                    reported_transaction=instance)
            except BaseException:
                models.TransactionSector.objects.create(
                    transaction=instance,
                    reported_transaction=instance,
                    percentage=100,
                    **sector_data
                )

        if recipient_country_data.get('country'):
            try:
                models.TransactionRecipientCountry.objects.get(
                    reported_transaction=instance,
                )
            except BaseException:
                models.TransactionRecipientCountry.objects.create(
                    transaction=instance,
                    reported_transaction=instance,
                    percentage=100,
                    **recipient_country_data
                )

        if recipient_region_data.get('region'):
            try:
                models.TransactionRecipientRegion.objects.get(
                    transaction=instance,
                    reported_transaction=instance)
            except BaseException:
                models.TransactionRecipientRegion.objects.create(
                    transaction=instance,
                    reported_transaction=instance,
                    percentage=100,
                    **recipient_region_data
                )

        return update_instance
