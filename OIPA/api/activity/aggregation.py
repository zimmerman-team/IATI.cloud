from rest_framework import serializers
from api.generics.serializers import DynamicFieldsSerializer
from api.generics import utils
from api.generics.filters import BasicFilterBackend
from api.activity.filters import ActivityFilter
from api.generics.serializers import NoCountPaginationSerializer

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
    expenditure = serializers.DecimalField(
        source='aggregate_expenditure',
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


class AggregationsPaginationSerializer(NoCountPaginationSerializer):
    """PaginationSerializer with aggregations for a list of activities."""
    aggregations = AggregationsSerializer(
        source='paginator.object_list',
        query_field='aggregations',
        fields=()
    )
