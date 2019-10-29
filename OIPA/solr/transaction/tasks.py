# If on Python 2.X
from __future__ import print_function

import pysolr

from solr.tasks import BaseTaskIndexing

from iati.transaction.models import Transaction
from solr.transaction.indexing import TransactionIndexing

solr = pysolr.Solr('http://localhost:8983/solr/transaction', always_commit=True)


class TransactionTaskIndexing(BaseTaskIndexing):
    indexing = TransactionIndexing
    model = Transaction

    def run_from_activity(self, activity):
        for transaction in activity.transaction_set.all():
            self.instance = transaction
            self.run()
