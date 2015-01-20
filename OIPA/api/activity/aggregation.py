from rest_framework import serializers
from api.generics.serializers import DynamicFieldsSerializer
from api.generics import utils
from api.generics.filters import BasicFilterBackend
from api.activity.filters import ActivityFilter


class AggregationsSerializer(DynamicFieldsSerializer):
    filter_class = ActivityFilter

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

    def to_representation(self, queryset):
        query_params = utils.query_params_from_context(self.context)
        if query_params:
            params = utils.get_type_parameters('activity-filter', query_params)
            filter_class = self.filter_class()
            queryset = filter_class.filter_queryset(queryset, params)

        return super(AggregationsSerializer, self).to_representation(queryset)
