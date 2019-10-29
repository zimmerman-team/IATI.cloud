# If on Python 2.X
from __future__ import print_function

import pysolr

from iati.transaction.models import Transaction
from solr.transaction.indexing import TransactionIndexing

solr = pysolr.Solr('http://localhost:8983/solr/transaction', always_commit=True)


class TransactionTaskIndexing(object):
    transaction = None

    def __init__(self, transaction=None):
        self.transaction = transaction

    def run_indexing(self):
        solr.add([TransactionIndexing(self.transaction).data])

    def delete_indexing(self):
        solr.delete(q='id:{id}'.format(id=self.transaction.id))

    def run_indexing_from_activity(self, activity):
        for transaction in activity.transaction_set.all():
            self.transaction = transaction
            self.run_indexing()

    def run_all_indexing(self):
        for transaction in Transaction.objects.all():
            self.transaction = transaction
            self.run_indexing()

