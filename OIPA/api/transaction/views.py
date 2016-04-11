from api.transaction.serializers import TransactionSerializer
from api.transaction.filters import TransactionFilter
from iati.transaction.models import Transaction
from api.generics.views import DynamicListView, DynamicDetailView

from rest_framework.filters import DjangoFilterBackend
from rest_framework.generics import GenericAPIView

class TransactionList(DynamicListView):
    """
    Returns a list of IATI Transactions stored in OIPA.

    ## Request parameters

    - `id` (*optional*): Transaction identifier.
    - `aid_type` (*optional*): Aid type identifier.
    - `activity` (*optional*): Comma separated list of activity id's.
    - `transaction_type` (*optional*): Transaction type identifier.
    - `value` (*optional*): Transaction value.
    - `min_value` (*optional*): Minimal transaction value.
    - `max_value` (*optional*): Maximal transaction value.
    - `q` (*optional*): Search specific value in activities list.
        See [Searching]() section for details.
    - `fields` (*optional*): List of fields to display.

    ## Searching

    - `description`
    - `provider_organisation_name`
    - `receiver_organisation_name`

    ## Result details

    Each result item contains short information about transaction including URI to transaction details.

    URI is constructed as follows: `/api/transactions/{transaction_id}`

    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filter_class = TransactionFilter

    fields = (
        'url',
        'activity',
        'provider_organisation',
        'receiver_organisation',
        'currency',
        'transaction_type',
        'value_date',
        'value',
    )

    search_fields = (
        'description',
        'provider_organisation',
        'receiver_organisation',
    )

class TransactionDetail(DynamicDetailView):
    """
    Returns detailed information about Transaction.

    ## URI Format

    ```
    /api/transactions/{transaction_id}
    ```

    ### URI Parameters

    - `transaction_id`: Numerical ID of desired Transaction

    ## Request parameters

    - `fields` (*optional*): List of fields to display

    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

from django.db.models import Count, Sum, Q, F

from api.activity.filters import SearchFilter
from api.generics.aggregation import aggregate, Aggregation, GroupBy, Order, intersection
from api.generics.aggregation import AggregationView

from geodata.models import Country
from api.country.serializers import CountrySerializer

from iati.models import Activity
from iati.models import ActivityParticipatingOrganisation
from iati.models import ActivityReportingOrganisation

class TransactionAggregation(AggregationView):
    """
    Returns aggregations based on the item grouped by, and the selected aggregation.

    ## Group by options

    API request has to include `group_by` parameter.
    
    This parameter controls result aggregations and
    can be one or more (comma separated values) of:

    - `recipient_country`
    - `recipient_region`
    - `sector`
    - `reporting_organisation`
    - `participating_organisation_ref`
    - `participating_organisation_name`
    - `activity_status`
    - `policy_marker`
    - `collaboration_type`
    - `default_flow_type`
    - `default_aid_type`
    - `default_finance_type`
    - `default_tied_status`
    - `budget_per_year`
    - `budget_per_quarter`
    - `transactions_per_quarter`
    - `transaction_date_year`

    ## Aggregation options

    API request has to include `aggregations` parameter.
    
    This parameter controls result aggregations and
    can be one or more (comma separated values) of:

    - `count`
    - `budget`
    - `disbursement`
    - `expenditure`
    - `commitment`
    - `incoming_fund`
    - `transaction_value`
    - `recipient_country_percentage_weighted_incoming_fund` (only in combination with recipient_country group_by)
    - `recipient_country_percentage_weighted_disbursement` (only in combination with transaction based group_by's)
    - `recipient_country_percentage_weighted_expenditure` (only in combination with transaction based group_by's)
    - `sector_percentage_weighted_budget` (only in combination with budget based group_by's)
    - `sector_percentage_weighted_incoming_fund` (only in combination with transaction based group_by's)
    - `sector_percentage_weighted_disbursement` (only in combination with transaction based group_by's)
    - `sector_percentage_weighted_expenditure` (only in combination with transaction based group_by's)
    - `sector_percentage_weighted_budget` (only in combination with budget based group_by's)

    ## Request parameters

    All filters available on the Activity List, can be used on aggregations.

    """

    queryset = Transaction.objects.all()

    filter_backends = (SearchFilter, DjangoFilterBackend,)
    filter_class = TransactionFilter

    allowed_aggregations = (
        Aggregation(
            query_param='count',
            field='count',
            annotate=Count('id'),
        ),
        Aggregation(
            query_param='budget',
            field='budget',
            annotate=Sum('activity__budget__value'),
        ),
    )

    allowed_groupings = (
        GroupBy(
            query_param="recipient_country",
            fields="activity__recipient_country",
            queryset=Country.objects.all(),
            serializer=CountrySerializer,
            serializer_fields=('url', 'code', 'name', 'location'),
        ),
        GroupBy(
            query_param="reporting_organisation",
            fields="activity__reporting_organisations__normalized_ref",
            renamed_fields="reporting_organisation",
            queryset=ActivityReportingOrganisation.objects.all(),
            # serializer=CountrySerializer,
            # serializer_fields=('url', 'code', 'name', 'location'),
        ),
    )

