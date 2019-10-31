# If on Python 2.X
from __future__ import print_function

import pysolr
from django.conf import settings

from geodata.models import Country
from solr.codelists.country.indexing import CountryIndexing
from solr.tasks import BaseTaskIndexing

solr = pysolr.Solr(
    '{url}/{core}'.format(
        url=settings.SOLR.get('url'),
        core=settings.SOLR.get('cores').get('codelist').country('country')
    ), always_commit=True
)


class CodeListCountryTaskIndexing(BaseTaskIndexing):
    indexing = CountryIndexing
    model = Country
    solr = solr
