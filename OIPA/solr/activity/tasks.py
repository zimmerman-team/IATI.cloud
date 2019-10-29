# If on Python 2.X
from __future__ import print_function

import pysolr

from solr.tasks import BaseTaskIndexing

from iati.models import Activity
from solr.transaction.tasks import TransactionTaskIndexing
from solr.activity.indexing import ActivityIndexing

solr = pysolr.Solr('http://localhost:8983/solr/activity', always_commit=True)


class ActivityTaskIndexing(BaseTaskIndexing):
    indexing = ActivityIndexing
    model = Activity

    def run_related(self):
        TransactionTaskIndexing().run_from_activity(self.instance)
