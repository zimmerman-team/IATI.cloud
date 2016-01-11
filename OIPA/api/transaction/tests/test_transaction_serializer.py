# TODO: actually create these tests
from django.test import RequestFactory
from django.core.urlresolvers import reverse
from api.transaction.serializers import TransactionSerializer
from iati.transaction.factories import TransactionFactory

from django.test import TestCase as DjangoTestCase # Runs each test in a transaction and flushes database
from unittest import TestCase
import datetime

from django.test import RequestFactory
from iati.factory import iati_factory
from api.activity import serializers

class TransactionSerializerTestCase(DjangoTestCase):
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
