import json
from solr.base import IndexingSerializer, DocumentLinkSerializer
from solr.utils import bool_string, value_string, decimal_string, \
    get_narrative_lang_list, add_reporting_org, get_child_attr
from solr.activity.serializers import ActivitySectorSerializer


class ResultSerializer(IndexingSerializer):

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
            self.add_field('result_document_link', [])

            for document_link in document_link_all:
                self.add_value_list('result_document_link', json.dumps(DocumentLinkSerializer(document_link).data))

    def to_representation(self, result):
        self.record = result

        self.indexing = {}
        self.representation = {}

        self.result()
        self.build()

        return self.representation
