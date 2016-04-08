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

class ActivityAggregations(GenericAPIView):
    """
    """

    queryset = Transaction.objects.all()

    filter_backends = (DjangoFilterBackend,)
    filter_class = TransactionFilter

    # allowed aggregations...
    allowed_aggregations = (
        
    )

    # allowed group_by's...
    allowed_groupings = (

    )

    # allowed order_by's...
    allowed_orderings = (

    )


    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # results = ActivityAggregationSerializer(
        #     queryset,
        #     context=self.get_serializer_context())

        return aggregate(queryset,
            request, 
            self.allowed_aggregations, 
            self.allowed_groupings, 
            self.allowed_orderings,
        )

        # if results.data:
        #     if isinstance(results.data, dict) and results.data.get('error_message'):
        #         return Response({'count': 0, 'error': results.data.get('error_message'), 'results': []})
        #     return Response(results.data)
        # else:
        #     return Response({'count': 0, 'results': []})


