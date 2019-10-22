# If on Python 2.X
from __future__ import print_function

import pysolr

from iati.models import Activity
from solr.serializers import ActualSerializer

# Create a client instance. The timeout and authentication options are not required.
solr = pysolr.Solr('http://localhost:8983/solr/activity', always_commit=True)


def run():
    for activity in Activity.objects.all():
        solr.add(ActualSerializer(activity).data)
