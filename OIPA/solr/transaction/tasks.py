# If on Python 2.X
from __future__ import print_function

import pysolr
from django.conf import settings

from iati.transaction.models import Transaction
from solr.tasks import BaseTaskIndexing
from solr.transaction.indexing import TransactionIndexing
from solr.transaction_sector.tasks import TransactionSectorTaskIndexing

solr = pysolr.Solr(
    '{url}/{core}'.format(
        url=settings.SOLR.get('url'),
        core=settings.SOLR.get('cores').get('transaction')
    ), always_commit=True, timeout=180
)


class TransactionTaskIndexing(BaseTaskIndexing):
    indexing = TransactionIndexing
    model = Transaction
    solr = solr

    def run_from_activity(self, activity):
        for transaction in activity.transaction_set.all():
            self.instance = transaction
            self.run()
            # TransactionSectorTaskIndexing().run_from_transaction(transaction)
