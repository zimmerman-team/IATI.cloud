from solr.indexing import BaseIndexing
from solr.utils import decimal_string


class ActivitySectorIndexing(BaseIndexing):

    def sector(self):
        activity_sector = self.record
        if activity_sector:
            self.add_field('id', activity_sector.id)
            self.add_field('iati_identifier', activity_sector.activity.iati_identifier)
            self.add_field('sector_vocabulary', activity_sector.vocabulary_id)
            self.add_field('sector_vocabulary_uri', activity_sector.vocabulary_uri)
            self.add_field('sector_code', activity_sector.sector.code)
            self.add_field('sector_percentage', activity_sector.percentage)

            # self.related_narrative(
            #     activity_sector,
            #     'sector_narrative',
            #     'sector_narrative_text',
            #     'sector_narrative_lang'
            # )

    def to_representation(self, activity_sector):
        self.record = activity_sector
        self.indexing = {}
        self.representation = {}

        self.sector()
        self.build()

        return self.representation
