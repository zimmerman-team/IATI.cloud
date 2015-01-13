import django_filters
from api.generics.views import DynamicListAPIView
from api.generics.views import DynamicRetrieveAPIView
from api.transaction.serializers import TransactionSerializer
from iati.models import Transaction


class TransactionDetail(DynamicRetrieveAPIView):
    """
    Returns detailed information about Transaction.

    Parameters:

    - **`id`**: Numerical ID of desired Transaction
    - `fields` (*optional*): List of fields to display

    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class TransactionFilter(django_filters.FilterSet):
    """
    Transaction filter class
    """
    class Meta:
        model = Transaction
        fields = {
            'id': ['exact', ],
            'aid_type': ['exact', ],
            'transaction_type': ['exact', ],
            'value': ['exact', 'gte', 'lte'],
        }


class TransactionList(DynamicListAPIView):
    """
    Returns a list of IATI Transactions stored in OIPA.

    Parameters:

    - `id` (*optional*): Transaction identifier
    - `aid_type` (*optional*): Aid type identifier
    - `transaction_type` (*optional*): Transaction type identifier
    - `value` (*optional*): Transaction value.
      Possible options `value`, `value__gte`, `value__lte`
    - `fields` (*optional*): List of fields to display

    Searching is performed on fields:

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
