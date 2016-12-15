from rest_framework import serializers

from iati import models as iati_models
from iati.transaction import models

from api.generics.serializers import DynamicFieldsModelSerializer
from api.codelist.serializers import CodelistSerializer, NarrativeSerializer, VocabularySerializer
from api.activity.serializers import ActivitySerializer

from api.sector.serializers import SectorSerializer
from api.region.serializers import RegionSerializer, BasicRegionSerializer
from api.country.serializers import CountrySerializer

from api.generics.utils import get_or_raise

from api.activity.serializers import save_narratives, handle_errors

from iati.parser import validators
from iati.parser import exceptions

class TransactionProviderSerializer(serializers.ModelSerializer):
    ref = serializers.CharField()
    type = CodelistSerializer()
    narratives = NarrativeSerializer(many=True)
    provider_activity = serializers.HyperlinkedRelatedField(
        read_only=True,
        view_name='activities:activity-detail')
    provider_activity_id = serializers.CharField(source="provider_activity_ref", required=False)

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
    receiver_activity_id = serializers.CharField(source="receiver_activity_ref")

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

    transaction = serializers.CharField(write_only=True)

    def full_clean(self): # super(MyForm, self).clean() #if necessary
        # if self.cleaned_data.get('film') and 'director' in self._errors:
        #     del self._errors['director']
        return self.cleaned_data    

    class Meta:
        model = models.TransactionSector
        fields = (
            'transaction',
            'id',
            'sector',
            'vocabulary',
            'vocabulary_uri',
        )

    def validate(self, data):
        transaction = get_or_raise(models.Transaction, data, 'transaction')

        validated = validators.transaction_sector(
            transaction,
            data.get('sector', {}).get('code'),
            data.get('vocabulary', {}).get('code'),
            data.get('vocabulary_uri'),
        )

        return handle_errors(validated)

    def create(self, validated_data):
        transaction = validated_data.get('transaction')

        instance = models.TransactionSector.objects.create(**validated_data)

        return instance


    def update(self, instance, validated_data):
        transaction = validated_data.get('transaction')

        update_instance = models.TransactionSector(**validated_data)
        update_instance.id = instance.id
        update_instance.save()

        return update_instance


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
    provider_organisation = TransactionProviderSerializer()
    receiver_organisation = TransactionReceiverSerializer()
    disbursement_channel = CodelistSerializer()
    sector = TransactionSectorSerializer(many=True, required=False, source="transactionsector_set")
    recipient_countries = TransactionRecipientCountrySerializer(many=True, required=False, source="transactionrecipientcountry_set")
    recipient_regions = TransactionRecipientRegionSerializer(many=True, required=False, source="transactionrecipientregion_set")
    tied_status = CodelistSerializer()
    transaction_type = CodelistSerializer()
    currency = CodelistSerializer()
    description = TransactionDescriptionSerializer()
    humanitarian = serializers.BooleanField()

    activity = ActivitySerializer(read_only=True, fields=('id', 'url'))
    activity_id = serializers.CharField(write_only=True)

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
            'recipient_countries',
            'recipient_regions',
            'flow_type',
            'finance_type',
            'aid_type',
            'tied_status',
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
            # data.get('sector', {}).get('code'),
            # data.get('sector', {}).get('vocabulary'),
            # data.get('sector', {}).get('vocabulary_uri'),
            data.get('recipient_country', {}).get('code'),
            data.get('recipient_region', {}).get('code'),
            data.get('recipient_region', {}).get('vocabulary'),
            data.get('recipient_region', {}).get('vocabulary_uri'),
            data.get('flow_type', {}).get('code'),
            data.get('finance_type', {}).get('code'),
            data.get('aid_type', {}).get('code'),
            data.get('tied_status', {}).get('code'),
        )

        return handle_errors(validated)


    def create(self, validated_data):
        activity = validated_data.get('activity')
        description_narratives_data = validated_data.pop('description_narratives', [])
        provider_data = validated_data.pop('provider_org')
        provider_narratives_data = validated_data.pop('provider_org_narratives', [])
        receiver_data = validated_data.pop('receiver_org')
        receiver_narratives_data = validated_data.pop('receiver_org_narratives', [])
        # sector_data = validated_data.pop('sector')
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

        # if sector_data.get('sector'):
        #     models.TransactionSector.objects.create(
        #         transaction=instance,
        #         **sector_data
        #         )

        if recipient_country_data.get('country'):
            models.TransactionRecipientCountry.objects.create(
                transaction=instance,
                percentage=100,
                **recipient_country_data
                )

        if recipient_region_data.get('region'):
            models.TransactionRecipientRegion.objects.create(
                transaction=instance,
                percentage=100,
                **recipient_region
                )

        return instance


    def update(self, instance, validated_data):
        activity = validated_data.get('activity')
        description_narratives_data = validated_data.pop('description_narratives', [])
        provider_data = validated_data.pop('provider_org')
        provider_narratives_data = validated_data.pop('provider_org_narratives', [])
        receiver_data = validated_data.pop('receiver_org')
        receiver_narratives_data = validated_data.pop('receiver_org_narratives', [])
        # sector_data = validated_data.pop('sector')
        recipient_country_data = validated_data.pop('recipient_country')
        recipient_region_data = validated_data.pop('recipient_region')

        update_instance = models.Transaction(**validated_data)
        update_instance.id = instance.id
        update_instance.save()

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

        # if sector_data.get('sector'):
        #     models.TransactionSector.objects.create(
        #         transaction=instance,
        #         **sector_data
        #         )

        if recipient_country_data.get('country'):
            models.TransactionRecipientCountry.objects.create(
                transaction=instance,
                percentage=100,
                **recipient_country_data
                )

        if recipient_region_data.get('region'):
            models.TransactionRecipientRegion.objects.create(
                transaction=instance,
                percentage=100,
                **recipient_region
                )


        return update_instance


