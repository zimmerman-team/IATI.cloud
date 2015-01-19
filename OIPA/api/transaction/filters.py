import django_filters
from iati.models import Transaction


class TransactionFilter(django_filters.FilterSet):
    """
    Transaction filter class
    """
    min_value = django_filters.NumberFilter(name='value', lookup_type='gte')
    max_value = django_filters.NumberFilter(name='value', lookup_type='lte')

    class Meta:
        model = Transaction
        fields = [
            'id',
            'aid_type',
            'activity__id',
            'transaction_type',
            'value',
            'min_value',
            'max_value',
        ]
