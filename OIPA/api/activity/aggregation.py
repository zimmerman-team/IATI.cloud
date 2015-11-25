from rest_framework import serializers
from api.generics.serializers import DynamicFieldsSerializer
from api.generics import utils
from api.generics.filters import BasicFilterBackend
from api.activity.filters import ActivityFilter
from api.generics.serializers import NoCountPaginationSerializer
from rest_framework.response import Response
from collections import OrderedDict

class AggregationsSerializer(DynamicFieldsSerializer):
    # TODO: rewrite as activity annotations

    # total_budget = serializers.DecimalField(
    #     source='aggregate_total_budget',
    #     max_digits=15,
    #     decimal_places=2,
    #     coerce_to_string=False
    # )

    budget = serializers.DecimalField(
        source='aggregate_budget',
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
    
    # title = serializers.IntegerField(source='aggregate_title')

class AggregationsPaginationSerializer(NoCountPaginationSerializer):
    """PaginationSerializer with aggregations for a list of activities."""

    def paginate_queryset(self, queryset, request, view=None):
        self.aggregations = AggregationsSerializer(queryset, 
            # query_field='aggregations', 
            # fields=(),
            context={
                'request': request,
            },
        )
        return super(AggregationsPaginationSerializer, self).paginate_queryset(queryset, request, view)
    
    def get_paginated_response(self, data):

        # if (self.aggregations.data):
        #     return Response(OrderedDict([
        #         ('count', self.page.paginator.count),
        #         ('next', self.get_next_link()),
        #         ('previous', self.get_previous_link()),
        #         ('aggregations', self.aggregations.data),
        #         ('results', data),
        #     ]))
        # else:
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data),
        ]))
