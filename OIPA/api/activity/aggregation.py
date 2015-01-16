from rest_framework import serializers
from api.generics.serializers import DynamicFieldsSerializer


class AggregationsSerializer(DynamicFieldsSerializer):
    total_budget = serializers.DecimalField(
        source='aggregate_total_budget',
        max_digits=15,
        decimal_places=2,
        coerce_to_string=False
    )
    count = serializers.IntegerField()
    disbursement = serializers.DecimalField(
        source='aggregate_disbursement',
        max_digits=999,
        decimal_places=2,
        coerce_to_string=False
    )
    commitment = serializers.DecimalField(
        source='aggregate_commitment',
        max_digits=999,
        decimal_places=2,
        coerce_to_string=False
    )
    title = serializers.IntegerField(source='aggregate_title')
