# If on Python 2.X
from __future__ import print_function

import pysolr

from iati.models import Activity
from solr.transaction.tasks import TransactionTaskIndexing
from solr.activity.indexing import ActivityIndexing

solr = pysolr.Solr('http://localhost:8983/solr/activity', always_commit=True)


class ActivityTaskIndexing(object):
    activity = None
    related_indexing = False

    def __init__(self, activity, related_indexing=False):
        self.activity = activity
        self.related_indexing = related_indexing

    def run_indexing(self):
        solr.add([ActivityIndexing(self.activity).data])

        if self.related_indexing:
            TransactionTaskIndexing().run_indexing_from_activity(self.activity)

    def delete_indexing(self):
        solr.delete(q='id:{id}'.format(id=self.activity.id))

    def run_all_indexing(self):
        for activity in Activity.objects.all():
            self.activity = activity
            self.run_indexing()
