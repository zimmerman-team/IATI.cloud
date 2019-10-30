from solr.indexing import BaseIndexing
from solr.utils import get_child_attr


class DatasetNoteIndexing(BaseIndexing):

    def dataset_note(self):
        dataset_note = self.record

        self.add_field('id', dataset_note.id)
        self.add_field('iati_identifier', dataset_note.iati_identifier)
        self.add_field('exception_type', dataset_note.exception_type)
        self.add_field('model', dataset_note.model)
        self.add_field('field', dataset_note.field)
        self.add_field('message', dataset_note.message)
        self.add_field('line_number', dataset_note.line_number)
        self.add_field('variable', dataset_note.variable)
        self.add_field('publisher_iati_id', get_child_attr(dataset_note, '.dataset.publisher.publisher_iati_id'))
        self.add_field('publisher_name', get_child_attr(dataset_note, '.dataset.publisher.name'))
        self.add_field('publisher_name', get_child_attr(dataset_note, '.dataset.publisher.display_name'))

    def to_representation(self, dataset_note):
        self.record = dataset_note

        self.indexing = {}
        self.representation = {}

        self.dataset_note()
        self.build()

        return self.representation
