from rest_framework import serializers
from iati.models import Budget
from api.generics.serializers import (
    ModelSerializerNoValidation
)
from api.activity.serializers import (
    ValueSerializer, CodelistSerializer, ActivitySectorSerializer,
    RecipientCountrySerializer, ActivityRecipientRegionSerializer
)


class BudgetSerializer(ModelSerializerNoValidation):

    value = ValueSerializer(source='*')
    type = CodelistSerializer()
    status = CodelistSerializer()

    activity = serializers.CharField(write_only=True)

    # because we want to validate in the validator instead
    period_start = serializers.CharField()
    period_end = serializers.CharField()

    activity_id = serializers.CharField(
        source='activity.iati_identifier',
        read_only=True
    )
    sectors = ActivitySectorSerializer(
        many=True,
        source='activity.activitysector_set',
        read_only=True,
        required=False,
    )
    recipient_countries = RecipientCountrySerializer(
        many=True,
        source='activity.activityrecipientcountry_set',
        read_only=True,
        required=False,
    )
    recipient_regions = ActivityRecipientRegionSerializer(
        many=True,
        source='activity.activityrecipientregion_set',
        read_only=True,
        required=False,
    )

    iati_identifier = serializers.CharField(source='activity.iati_identifier', required=False)  # NOQA: E501

    class Meta:
        model = Budget
        # filter_class = BudgetFilter
        fields = (
            'activity',
            'id',
            'type',
            'status',
            'period_start',
            'period_end',
            'value',
            'sectors',
            'recipient_countries',
            'recipient_regions',
            'iati_identifier',
            # TODO: update test (if it exists):
            'xdr_value',
            'usd_value',
            'eur_value',
            'gbp_value',
            'jpy_value',
            'cad_value',
            'activity_id'
        )
