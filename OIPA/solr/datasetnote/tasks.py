# If on Python 2.X
from __future__ import print_function

import pysolr
from django.conf import settings

from solr.tasks import BaseTaskIndexing

from iati_synchroniser.models import DatasetNote
from solr.datasetnote.indexing import DatasetNoteIndexing

solr = pysolr.Solr(
    '{url}/{core}'.format(
        url=settings.SOLR.get('url'),
        core=settings.SOLR.get('cores').get('datasetnote')
    ), always_commit=True
)


class DatasetNoteTaskIndexing(BaseTaskIndexing):
    indexing = DatasetNoteIndexing
    model = DatasetNote
    solr = solr
