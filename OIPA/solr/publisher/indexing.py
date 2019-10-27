from solr.base import BaseIndexing


class PublisherIndexing(BaseIndexing):

    def publisher(self):
        publisher = self.record

        self.add_field('id', publisher.id)
        self.add_field('publisher_iati_id', publisher.iati_id)
        self.add_field('publisher_name', publisher.name)
        self.add_field('publisher_display_name', publisher.display_name)

    def to_representation(self, publisher):
        self.record = publisher
        self.indexing = {}
        self.representation = {}

        self.publisher()
        self.build()

        return self.representation
