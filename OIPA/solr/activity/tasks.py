# If on Python 2.X
from __future__ import print_function

import pysolr
from django.conf import settings

from iati.models import Activity
from solr.activity.indexing import ActivityIndexing
from solr.budget.tasks import BudgetTaskIndexing
from solr.result.tasks import ResultTaskIndexing
from solr.tasks import BaseTaskIndexing
from solr.transaction.tasks import TransactionTaskIndexing
from solr.activity_sector.tasks import ActivitySectorTaskIndexing

solr = pysolr.Solr(
    '{url}/{core}'.format(
        url=settings.SOLR.get('url'),
        core=settings.SOLR.get('cores').get('activity')
    ), always_commit=True
)


class ActivityTaskIndexing(BaseTaskIndexing):
    indexing = ActivityIndexing
    model = Activity
    solr = solr

    def run_related(self):
        TransactionTaskIndexing().run_from_activity(self.instance)
        BudgetTaskIndexing().run_from_activity(self.instance)
        ResultTaskIndexing().run_from_activity(self.instance)
        ActivitySectorTaskIndexing().run_from_activity(self.instance)
