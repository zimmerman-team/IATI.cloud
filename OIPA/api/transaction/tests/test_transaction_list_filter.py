from django.test import TestCase
from iati.models import Transaction
from iati.factory.iati_factory import ActivityFactory
from iati.transaction.factories import TransactionTypeFactory
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
        activity = ActivityFactory()
        transaction_type = TransactionTypeFactory(code=1)
        self.transactions = dict(
            value_100=TransactionFactory(id=1,
                                         value=100,
                                         activity=activity,
                                         transaction_type=transaction_type),
            value_150=TransactionFactory(id=2,
                                         value=150,
                                         activity=activity,
                                         transaction_type=transaction_type),
            value_200=TransactionFactory(id=3,
                                         value=200,
                                         activity=activity,
                                         transaction_type=transaction_type),
        )

    def test_if_max_value_filter_applied(self):
        """
        Test if min_value
        """
        queryset = Transaction.objects
        filtered = TransactionFilter({'max_value': 150}, queryset=queryset)
        self.assertQuerysetEqual(
            filtered.qs,
            [t.pk for t in queryset.filter(value__lte=150).all()],
            lambda t: t.pk,
            ordered=False)

    def test_if_min_value_filter_applied(self):
        """
        Test if min_value
        """
        queryset = Transaction.objects
        filtered = TransactionFilter({'min_value': 150}, queryset=queryset)
        self.assertQuerysetEqual(
            filtered.qs,
            [t.pk for t in queryset.filter(value__gte=150).all()],
            lambda t: t.pk,
            ordered=False)
