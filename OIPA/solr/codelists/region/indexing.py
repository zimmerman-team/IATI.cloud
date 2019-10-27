from solr.base import BaseIndexing


class RegionIndexing(BaseIndexing):

    def region(self):
        region = self.record

        self.add_field('id', region.code)
        self.add_field('code', region.code)
        self.add_field('name', region.name)

    def to_representation(self, region):
        self.record = region
        self.indexing = {}
        self.representation = {}

        self.region()
        self.build()

        return self.representation
