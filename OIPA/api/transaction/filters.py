import django_filters
from iati.models import Transaction


class TransactionFilter(django_filters.FilterSet):
    """
    Transaction filter class
    """
    value_min = django_filters.NumberFilter(name='value', lookup_type='gte')
    value_max = django_filters.NumberFilter(name='value', lookup_type='lte')

    class Meta:
        model = Transaction
        fields = [
            'id',
            'aid_type',
            'transaction_type',
            'value',
            'value_min',
            'value_max',
        ]
