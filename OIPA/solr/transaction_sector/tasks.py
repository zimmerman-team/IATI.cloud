# If on Python 2.X
from __future__ import print_function

import pysolr
from django.conf import settings

from solr.tasks import BaseTaskIndexing
from solr.transaction_sector.indexing import TransactionSectorIndexing

solr = pysolr.Solr(
    '{url}/{core}'.format(
        url=settings.SOLR.get('url'),
        core=settings.SOLR.get('cores').get('transaction-sector')
    ), always_commit=True
)


class TransactionSectorTaskIndexing(BaseTaskIndexing):
    indexing = TransactionSectorIndexing
    solr = solr

    def run_from_transaction(self, transaction):
        for sectors in transaction.transactionsector_set.all():
            self.instance = sectors
            self.run()

    def delete(self):
        if settings.SOLR.get('indexing'):
            self.solr.delete(q='iati_identifier:{iati_identifier}'.format(
                iati_identifier=self.instance.transaction.activity
                                    .iati_identifier))
