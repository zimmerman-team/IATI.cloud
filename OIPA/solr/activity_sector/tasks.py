# If on Python 2.X
from __future__ import print_function

import pysolr
from django.conf import settings

from solr.activity_sector.indexing import ActivitySectorIndexing
from solr.tasks import BaseTaskIndexing

solr = pysolr.Solr(
    '{url}/{core}'.format(
        url=settings.SOLR.get('url'),
        core=settings.SOLR.get('cores').get('activity-sector')
    ), always_commit=True, timeout=180
)


class ActivitySectorTaskIndexing(BaseTaskIndexing):
    indexing = ActivitySectorIndexing
    solr = solr

    def run_from_activity(self, activity):
        for sectors in activity.activitysector_set.all():
            self.instance = sectors
            self.run()

    def delete(self):
        if settings.SOLR.get('indexing'):
            self.solr.delete(q='iati_identifier:{iati_identifier}'.format(
                iati_identifier=self.instance.activity.iati_identifier))
