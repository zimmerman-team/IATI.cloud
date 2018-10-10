from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from api.generics.filters import SearchFilter
from api.aggregation.views import Aggregation, AggregationView, GroupBy

from unesco.models import TransactionBalance
from api.unesco.filters import TransactionBalanceFilter
from iati.models import Sector, Activity, ActivitySector, Budget
from api.unesco.serializers import SectorBudgetAggregationSerializer


class TransactionBalanceAggregation(AggregationView):
    """
       Returns a list aggregations of the transaction balance of each activity for UNESCO specific.

       ## Request parameters
       - `reporting_organisation_identifier` (*optional*): Comma separated list of the reporting organisation id's.
       - `recipient_country` *optional*): Comma separated list of iso2 country codes.
       - `recipient_region` (*optional*): Comma separated list of region codes.
       - `sector` (*optional*): Comma separated list of 5-digit sector codes.
       - `participating_organisation_name` (*optional*): Comma separated list of organisation id's.
       - `sector_startswith_in` (*optional*): Comma separated list of prefix sector codes.
       - `transactionbalance_total_budget_lte` (*optional*): Less then or equal transaction balance of the total budget.
       - `transactionbalance_total_budget_gte` (*optional*): Greater then or equal transaction balance of the total budget.
       - `transactionbalance_total_expenditure_lte` (*optional*): Less then or equal transaction balance of the total expenditure.
       - `transactionbalance_total_expenditure_gte` (*optional*): Greater then or equal transaction balance of the total expenditure.
       - `activity_status` (*optional*): Comma separated list of activity statuses.
       - `planned_start_date_lte` (*optional*): Date in YYYY-MM-DD format, returns activities earlier or equal to the given activity date.
       - `planned_start_date_gte` (*optional*): Date in YYYY-MM-DD format, returns activities later or equal to the given activity date.
       - `planned_end_date_lte` (*optional*): Date in YYYY-MM-DD format, returns activities earlier or equal to the given activity date.
       - `planned_end_date_gte` (*optional*): Date in YYYY-MM-DD format, returns activities later or equal to the given activity date.


       ## Group by options

       API request has to include `group_by` parameter.

       This parameter controls result aggregations and
       can be one or more (comma separated values) of:
       - `reporting_organisation_identifier`
       - `activity_iati_identifier`


       ## Aggregation options

       API request has to include `aggregations` parameter.

       This parameter controls result aggregations and
       can be one or more (comma separated values) of:

       - `total_budget`
       - `total_expenditure`
       - `cumulative_budget`
       - `cumulative_expenditure`

    """

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
        GroupBy(
            query_param="activity_iati_identifier",
            fields="activity__iati_identifier",
            renamed_fields="activity_iati_identifier",
        ),
    )


class SectorBudgetAggregations(viewsets.ModelViewSet):
    queryset = Sector.objects.all()
    serializer_class = SectorBudgetAggregationSerializer
    budgets = None

    def get_queryset(self):
        activity_ids = ActivitySector.objects.filter(
            sector__code=self.request.query_params.get('sector')).values_list(
            'activity', flat=True).distinct()

        self.budgets = list(Budget.objects.filter(
            activity__id__in=activity_ids).values('activity__sector').annotate(
            total_budget=Sum('value')))

        sector_ids = ActivitySector.objects.filter(
            sector__code=self.request.query_params.get('sector')).values_list(
            'activity__sector', flat=True).distinct()

        return Sector.objects.filter(code__in=sector_ids)

