from solr.base import IndexingSerializer
from solr.utils import decimal_string


class ActivitySectorSerializer(IndexingSerializer):

    def activity_sector(self, activity_sector):
        self.add_field('vocabulary', activity_sector.vocabulary_id)
        self.add_field('vocabulary_uri', activity_sector.vocabulary_uri)

        self.add_field('code', activity_sector.sector_id)
        self.add_field('percentage', decimal_string(activity_sector.percentage))

    def to_representation(self, activity_sector):
        self.indexing = {}
        self.representation = {}

        self.activity_sector(activity_sector)
        self.build()

        return self.representation
