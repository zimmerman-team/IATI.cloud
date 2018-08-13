from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend

from api.generics.filters import SearchFilter
from api.aggregation.views import Aggregation, AggregationView, GroupBy

from unesco.models import TransactionBalance
from .filters import TransactionBalanceFilter


class TransactionBalanceAggregation(AggregationView):

    queryset = TransactionBalance.objects.all()
    filter_backends = (SearchFilter, DjangoFilterBackend, )
    filter_class = TransactionBalanceFilter

    allowed_aggregations = (
        Aggregation(
            query_param='total_budget',
            field='total_budget',
            annotate=Sum('total_budget'),
        ),
        Aggregation(
            query_param='total_expenditure',
            field='total_expenditure',
            annotate=Sum('total_expenditure'),
        ),
        Aggregation(
            query_param='cumulative_budget',
            field='cumulative_budget',
            annotate=Sum('cumulative_budget'),
        ),
        Aggregation(
            query_param='cumulative_expenditure',
            field='cumulative_expenditure',
            annotate=Sum('cumulative_expenditure'),
        ),
    )

    allowed_groupings = (
        GroupBy(
            query_param="reporting_organisation_identifier",
            fields="activity__publisher__publisher_iati_id",
            renamed_fields="reporting_organisation_identifier",
        ),
    )
