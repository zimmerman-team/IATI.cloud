# If on Python 2.X
from __future__ import print_function

import pysolr

# Create a client instance. The timeout and authentication options are not required.
solr = pysolr.Solr('http://localhost:8983/solr/activity', always_commit=True)
