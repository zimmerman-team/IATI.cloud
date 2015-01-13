import pytest
from django.test import RequestFactory
from django.core.urlresolvers import reverse
from api.transaction.serializers import TransactionSerializer
from iati.transaction.factories import TransactionFactory


class TestTransactionSerializer:
    """
    Test if transaction model is serialized correctly.
    """
    request_dummy = RequestFactory().get('/')
    transaction = TransactionFactory.build(id=1)

    def serialize_test_transaction(self, transaction=None):
        """
        Helper method simplifies tests of serialized data
        """
        return TransactionSerializer(
            transaction or self.transaction,
            context={'request': self.request_dummy},
        )

    @pytest.mark.django_db
    def test_transaction_serializer_has_correct_url(self):
        """
        Test if transactions serialized properly
        """
        serializer = self.serialize_test_transaction()
        assert 'url' in serializer.data.keys(), \
            """serialized data should include url"""

        expected_url = "http://testserver{reverse}".format(
            reverse=reverse('transactions:detail',
            args=(self.transaction.id,)))
        assert serializer.data.get('url', '') == expected_url, \
            """serialized url should point to transaction detail page"""
