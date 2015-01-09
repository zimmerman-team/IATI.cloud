from api.generics.views import DynamicListAPIView
from api.generics.views import DynamicRetrieveAPIView
from api.transaction.serializers import TransactionSerializer
from iati.models import Transaction


class TransactionDetail(DynamicRetrieveAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class TransactionList(DynamicListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    fields = (
        'id',
        'url'
        'activity_id',
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
