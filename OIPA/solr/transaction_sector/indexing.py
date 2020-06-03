from solr.indexing import BaseIndexing


class TransactionSectorIndexing(BaseIndexing):

    def sector(self):
        transaction_sector = self.record
        if transaction_sector:
            self.add_field('id', transaction_sector.id)
            self.add_field('iati_identifier',
                           transaction_sector.transaction.activity.iati_identifier)
            self.add_field('sector_vocabulary',
                           transaction_sector.vocabulary_id)
            self.add_field('sector_vocabulary_uri',
                           transaction_sector.vocabulary_uri)
            self.add_field('sector_code', transaction_sector.sector.code)
            self.add_field('sector_percentage', transaction_sector.percentage)

            # self.related_narrative(
            #     activity_sector,
            #     'sector_narrative',
            #     'sector_narrative_text',
            #     'sector_narrative_lang'
            # )

    def to_representation(self, transaction_sector):
        self.record = transaction_sector
        self.indexing = {}
        self.representation = {}

        self.sector()
        self.build()

        return self.representation
