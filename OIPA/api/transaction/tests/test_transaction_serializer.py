from django.core.urlresolvers import reverse
from api.transaction.serializers import TransactionSerializer
from iati.transaction.factories import TransactionFactory

from rest_framework import status
from rest_framework.test import APITestCase

from django.test import RequestFactory


class TransactionSerializerTestCase(APITestCase):
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

    def test_transaction_serializer_has_correct_url(self):
        """
        Test if transactions serialized properly
        """
        serializer = self.serialize_test_transaction()
        assert 'url' in serializer.data.keys(), \
            """serialized data should include url"""

        expected_url = "http://testserver{reverse}".format(
            reverse=reverse('transactions:transaction-detail',
            args=(self.transaction.id,)))
        assert serializer.data.get('url', '') == expected_url, \
            """serialized url should point to transaction detail page"""

    def test_transaction_detail_endpoint(self):
        """

        """
        transaction = TransactionFactory.create(id=2)
        url = reverse('transactions:transaction-detail', args={'2'})
        msg = 'activity transaction detail endpoint should be localed at {0}'
        expect_url = '/api/transactions/2/'
        assert url == expect_url, msg.format(expect_url)
        response = self.client.get(url)
        self.assertTrue(status.is_success(response.status_code))
