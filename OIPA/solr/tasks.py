# If on Python 2.X
from __future__ import print_function

import pysolr

solr = pysolr.Solr('', always_commit=True)


class BaseTaskIndexing(object):
    instance = None
    related = False
    indexing = None
    model = None

    def __init__(self, instance=None, related=False):
        self.instance = instance
        self.related = related

    def run_related(self):
        pass

    def run(self):
        solr.add([self.indexing(self.instance).data])

        if self.related:
            self.run_related()

    def delete(self):
        solr.delete(q='id:{id}'.format(id=self.instance.id))

    def run_all(self):
        for instance in self.model.objects.all():
            self.instance = instance
            self.run()
