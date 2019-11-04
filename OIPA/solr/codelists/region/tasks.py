# If on Python 2.X
from __future__ import print_function

import pysolr
from django.conf import settings

from geodata.models import Region
from solr.codelists.region.indexing import RegionIndexing
from solr.tasks import BaseTaskIndexing

solr = pysolr.Solr(
    '{url}/{core}'.format(
        url=settings.SOLR.get('url'),
        core=settings.SOLR.get('cores').get('codelist').get('region')
    ), always_commit=True
)


class CodeListRegionTaskIndexing(BaseTaskIndexing):
    indexing = RegionIndexing
    model = Region
    solr = solr
