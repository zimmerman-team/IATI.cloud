# If on Python 2.X
from __future__ import print_function

import pysolr
from django.conf import settings

from iati.models import Publisher
from solr.publisher.indexing import PublisherIndexing
from solr.tasks import BaseTaskIndexing

solr = pysolr.Solr(
    '{url}/{core}'.format(
        url=settings.SOLR.get('url'),
        core=settings.SOLR.get('cores').get('publisher')
    ), always_commit=True, timeout=180
)


class PublisherTaskIndexing(BaseTaskIndexing):
    indexing = PublisherIndexing
    model = Publisher
    solr = solr
