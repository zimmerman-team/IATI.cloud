from api.generics.views import DynamicListAPIView
from api.generics.views import DynamicRetrieveAPIView
from api.transaction.serializers import TransactionSerializer
from api.transaction.filters import TransactionFilter
from iati.models import Transaction


class TransactionDetail(DynamicRetrieveAPIView):
    """
    Returns detailed information about Transaction.

    ## URI Format:

    ```
    /api/transactions/{transaction_id}
    ```

    ### URI Parameters:

    - `transaction_id`: Numerical ID of desired Transaction

    ## Request parameters:

    - `fields` (*optional*): List of fields to display

    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class TransactionList(DynamicListAPIView):
    """
    Returns a list of IATI Transactions stored in OIPA.

    ## Request parameters:

    - `id` (*optional*): Transaction identifier
    - `aid_type` (*optional*): Aid type identifier
    - `transaction_type` (*optional*): Transaction type identifier
    - `value` (*optional*): Transaction value.
    - `min_value` (*optional*): Minimal transaction value
    - `max_value` (*optional*): Maximal transaction value
    - `fields` (*optional*): List of fields to display

    ## Searching is performed on fields:

    - `description`
    - `provider_organisation_name`
    - `receiver_organisation_name`

    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filter_class = TransactionFilter

    fields = (
        'id',
        'url',
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
