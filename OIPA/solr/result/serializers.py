import json
from solr.base import IndexingSerializer, DocumentLinkSerializer
from solr.utils import bool_string, add_reporting_org, get_child_attr


class ResultSerializer(IndexingSerializer):

    def document_link(self, document_link_all, prefix='result_document_link'):
        self.add_field(prefix, [])
        self.add_field(prefix + '_url', [])
        self.add_field(prefix + '_format', [])
        self.add_field(prefix + '_document_date_iso_date', [])
        self.add_field(prefix + '_description_narrative', [])
        self.add_field(prefix + '_category_code', [])
        self.add_field(prefix + '_language_code', [])

        for document_link in document_link_all:
            self.add_value_list(prefix, json.dumps(DocumentLinkSerializer(document_link).data))

            self.add_value_list(prefix + '_url', document_link.url)
            self.add_value_list(prefix + '_format', document_link.file_format_id)
            self.add_value_list(prefix + '_document_date_iso_date', document_link.iso_date)

            category_all = document_link.documentlinkcategory_set.all()
            if category_all:
                for category in category_all:
                    self.add_value_list(prefix + '_category_code', category.category_id)

            language_all = document_link.documentlinklanguage_set.all()
            if language_all:
                for language in language_all:
                    self.add_value_list(prefix + '_language_code', language.language_id)

    def result(self):
        self.add_field('iati_identifier', self.record.activity.iati_identifier)
        self.add_field('humanitarian', bool_string(get_child_attr(self.record, 'activity.humanitarian')))

        add_reporting_org(self, self.record.activity)

        title = get_child_attr(self.record, 'resulttitle')
        if title:
            self.narrative(title, 'result_title', True)

            self.add_field('result_title_narrative', [])
            for narrative in title.narratives.all():
                self.add_value_list('result_title_narrative', narrative.content)

        description = get_child_attr(self.record, 'resultdescription')
        if description:
            self.narrative(description, 'result_description', True)

            self.add_field('result_description_narrative', [])
            for narrative in title.narratives.all():
                self.add_value_list('result_description_narrative', narrative.content)

        document_link_all = self.record.documentlink_set.all()
        if document_link_all:
            self.document_link(document_link_all)

    def to_representation(self, result):
        self.record = result

        self.indexing = {}
        self.representation = {}

        self.result()
        self.build()

        return self.representation
