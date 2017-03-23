from django.db.models import Count, Sum

from rest_framework.filters import DjangoFilterBackend
from rest_framework import filters

from traceability.models import Chain, ChainNode, ChainNodeError, ChainLink, ChainLinkRelation
from iati.models import Activity, ActivityReportingOrganisation
from iati.transaction.models import Transaction

from api.generics.views import DynamicListView, DynamicDetailView
from api.pagination import CustomTransactionPagination

from api.organisation.serializers import OrganisationSerializer
from api.aggregation.views import AggregationView, Aggregation, GroupBy
from api.chain.filters import ChainFilter, ChainLinkFilter, ChainNodeErrorFilter
from api.chain.serializers import ChainSerializer, ChainLinkSerializer, ChainNodeErrorSerializer, ChainNodeSerializer
from api.activity.views import ActivityList
from api.transaction.serializers import TransactionSerializer
from api.transaction.filters import TransactionFilter


class ChainAggregations(AggregationView):
    """
    Returns aggregations based on the item grouped by, and the selected aggregation.

    ## Group by options

    API request has to include `group_by` parameter.
    
    This parameter controls result aggregations and
    can be one or more (comma separated values) of:

    - `tier`
    - `reporting_org`    

    ## Aggregation options

    API request has to include `aggregations` parameter.
    
    This parameter controls result aggregations and
    can be one or more (comma separated values) of:

    - `count` - node count

    ## Request parameters

    All filters available on the Chain List, can be used on aggregations.

    """

    queryset = ChainNode.objects.all()
    filter_backends = (DjangoFilterBackend, )
    filter_class = None

    allowed_aggregations = (
        Aggregation(
            query_param='count',
            field='count',
            annotate=Count('id', distinct=True),
        ),
    )

    allowed_groupings = (
        
        GroupBy(
            query_param="tier",
            fields=("tier",)
        ),
        GroupBy(
            query_param="reporting_organisation",
            fields=("activity__reporting_organisations__organisation__organisation_identifier", "activity__reporting_organisations__organisation__primary_name"),
            renamed_fields=("reporting_organisation_ref", "reporting_organisation_name"),
            queryset=ActivityReportingOrganisation.objects.all(),
        ),
    )


class ChainList(DynamicListView):
    """
    Returns a list of chains.

    ## Aggregations

    The [`  /chains/aggregations`](/api/chains/aggregations) endpoint can be used for chain based aggregations.

    ## Result details

    Each item contains all information on the chain link being shown.

    """

    queryset = Chain.objects.all()
    filter_backends = (DjangoFilterBackend, )
    filter_class = ChainFilter
    serializer_class = ChainSerializer

    fields = (
        'id',
        'url',
        'name',
        'last_updated'
    )


class ChainTransactionList(DynamicListView):
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
    pagination_class = CustomTransactionPagination

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

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Transaction.objects.filter(activity__id__in=Activity.objects.filter(chainnode__chain=pk))


class ChainDetail(DynamicDetailView):
    """
    Returns subpages of chains
    """
    queryset = Chain.objects.all()
    serializer_class = ChainSerializer

    fields = (
        'id',
        'url',
        'name',
        'last_updated',
        'links',
        'errors',
        'activities',
        'transactions',
        'nodes'
    )


class ChainLinkList(DynamicListView):
    """
    Returns a list of chain links.

    ## Request parameters
    - `chain` (*optional*): Comma separated list of chain names.
    - `tier` (*optional*): Comma separated list of tiers the link is in.

    ## Aggregations

    The /chains/aggregations endpoint can be used for chain based aggregations.

    ## Result details

    Each item contains all information on the chain link being shown.

    """

    queryset = ChainLink.objects.all()
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_class = ChainLinkFilter
    serializer_class = ChainLinkSerializer
    pagination_class = None

    ordering_fields = (
        'id',
    )
    fields = (
        'id',
        'start_node',
        'end_node',
        'relations')

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return ChainLink.objects.filter(chain=Chain.objects.get(pk=pk)).prefetch_related('relations').prefetch_related('start_node').prefetch_related('end_node')


class ChainNodeList(DynamicListView):
    """
    Returns a list of chain links.

    ## Request parameters
    - `chain` (*optional*): Comma separated list of chain names.
    - `tier` (*optional*): Comma separated list of tiers the link is in.

    ## Aggregations

    The /chains/aggregations endpoint can be used for chain based aggregations.

    ## Result details

    Each item contains all information on the chain link being shown.

    """

    queryset = ChainNode.objects.all()
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    serializer_class = ChainNodeSerializer
    pagination_class = None

    ordering_fields = (
        'id',
    )
    fields = (
        'id',
        'activity_oipa_id',
        'activity_iati_id',
        'tier',
        'bol',
        'eol')

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return ChainNode.objects.filter(chain=Chain.objects.get(pk=pk))


class ChainNodeErrorList(DynamicListView):
    """
    Returns a list of chain errors.
    """

    queryset = ChainNodeError.objects.all()
    filter_backends = (DjangoFilterBackend, )
    filter_class = ChainNodeErrorFilter
    serializer_class = ChainNodeErrorSerializer
    pagination_class = None

    fields = (
        'chain_node',
        'error_type',
        'mentioned_activity_or_org',
        'related_id',
        'warning_level'
    )

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return ChainNodeError.objects.filter(chain_node__chain=Chain.objects.get(pk=pk))


class ChainActivities(ActivityList):
    """
    Returns a list of activities
    """

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Activity.objects.filter(id__in=Activity.objects.filter(chainnode__chain=pk))



