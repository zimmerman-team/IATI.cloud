from solr.indexing import BaseIndexing


class CountryIndexing(BaseIndexing):

    def country(self):
        country = self.record

        self.add_field('id', country.code)
        self.add_field('code', country.code)
        self.add_field('name', country.name)

    def to_representation(self, country):
        self.record = country
        self.indexing = {}
        self.representation = {}

        self.country()
        self.build()

        return self.representation
