# If on Python 2.X
from __future__ import print_function

import pysolr
from django.conf import settings

from solr.tasks import BaseTaskIndexing

from iati.models import Budget
from solr.budget.indexing import BudgetIndexing

solr = pysolr.Solr(
    '{url}/{core}'.format(
        url=settings.SOLR.get('url'),
        core=settings.SOLR.get('cores').get('budget')
    ), always_commit=True
)


class BudgetTaskIndexing(BaseTaskIndexing):
    indexing = BudgetIndexing
    model = Budget
    solr = solr

    def run_from_activity(self, activity):
        for budget in activity.budget_set.all():
            self.instance = budget
            self.run()
