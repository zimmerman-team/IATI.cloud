from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from api.transaction.serializers import TransactionSerializer
from api.transaction.filters import TransactionFilter
from iati.transaction.models import Transaction


class TransactionDetail(RetrieveAPIView):
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


class TransactionList(ListAPIView):
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
        'id',
        'url',
        'activity',
        'aid_type',
        'description',
        'finance_type',
        'provider_organisation_name',
        'receiver_organisation_name',
        'transaction_date',
        'transaction_type',
        'value_date',
        'value',
        'currency',
    )

    search_fields = (
        'description',
        'provider_organisation_name',
        'receiver_organisation_name',
    )
