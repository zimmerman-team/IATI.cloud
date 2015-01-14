from django.test import TestCase
from iati.models import Transaction
from iati.transaction.factories import TransactionFactory
from api.transaction.filters import TransactionFilter


class TestTransactionListFiltering(TestCase):
    """
    Test transaction list filtering
    """

    def setUp(self):
        """
        Basic setup
        Creates 3 test transactions
        """
        self.transactions = dict(
            value_100=TransactionFactory.build(id=1, value=100),
            value_150=TransactionFactory.build(id=2, value=150),
            value_200=TransactionFactory.build(id=3, value=200),
        )

    def test_if_max_value_filter_applied(self):
        """
        Test if min_value
        """
        queryset = Transaction.objects
        filtered = TransactionFilter({'max_value': 150}, queryset=queryset)
        self.assertQuerysetEqual(filtered.qs,
                                 queryset.filter(value__lte=150),
                                 ordered=False)

    def test_if_min_value_filter_applied(self):
        """
        Test if min_value
        """
        queryset = Transaction.objects
        filtered = TransactionFilter({'min_value': 150}, queryset=queryset)
        self.assertQuerysetEqual(filtered.qs,
                                 queryset.filter(value__gte=150),
                                 ordered=False)
