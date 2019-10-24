import json
from solr.base import IndexingSerializer, DocumentLinkSerializer, ReferenceSerializer
from solr.utils import bool_string, add_reporting_org, get_child_attr


class ResultSerializer(IndexingSerializer):

    def field_narrative(self, field, key):
        if field:
            for narrative in field.narratives.all():
                self.add_value_list(key, narrative.content)

    def title(self):
        title = get_child_attr(self.record, 'resulttitle')
        if title:
            self.narrative(title, 'result_title', True)

            self.add_field('result_title_narrative', [])
            for narrative in title.narratives.all():
                self.add_value_list('result_title_narrative', narrative.content)

    def description(self):
        description = get_child_attr(self.record, 'resultdescription')
        if description:
            self.narrative(description, 'result_description', True)

            self.add_field('result_description_narrative', [])
            for narrative in description.narratives.all():
                self.add_value_list('result_description_narrative', narrative.content)

    def document_link(self, document_link_all, prefix='result_document_link'):
        if document_link_all:
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

    def reference(self, reference_all, prefix='result_reference', is_indicator=False):
        if reference_all:
            self.add_field(prefix, [])
            self.add_field(prefix + '_code', [])
            self.add_field(prefix + '_vocabulary', [])
            if not is_indicator:
                self.add_field(prefix + '_vocabulary_uri', [])
            else:
                self.add_field(prefix + '_indicator_uri', [])

            for reference in reference_all:
                self.add_value_list(prefix, json.dumps(ReferenceSerializer(reference).data))

                self.add_value_list(prefix + '_code', reference.code)
                self.add_value_list(prefix + '_vocabulary', reference.vocabulary_id)
                if not is_indicator:
                    self.add_value_list(prefix + '_vocabulary_uri', reference.vocabulary_uri)
                else:
                    self.add_value_list(prefix + '_indicator_uri', reference.indicator_uri)

    def indicator(self):
        indicator_all = self.record.resultindicator_set.all()
        if indicator_all:
            self.add_field('result_indicator', [])
            self.add_field('result_indicator_measure', [])
            self.add_field('result_indicator_ascending', [])
            self.add_field('result_indicator_aggregation_status', [])
            self.add_field('result_indicator_title_narrative', [])
            self.add_field('result_indicator_description_narrative', [])

            self.add_field('result_indicator_document_link_url', [])
            self.add_field('result_indicator_document_link_format', [])
            self.add_field('result_indicator_document_link_title_narrative', [])
            self.add_field('result_indicator_document_link_description_narrative', [])
            self.add_field('result_indicator_document_link_category_code', [])
            self.add_field('result_indicator_document_link_language_code', [])
            self.add_field('result_indicator_document_link_document_date_iso_date', [])

            for indicator in indicator_all:
                self.add_value_list('result_indicator_measure', indicator.measure_id)
                self.add_value_list('result_indicator_ascending', bool_string(indicator.ascending))
                self.add_value_list('result_indicator_aggregation_status', bool_string(indicator.aggregation_status))

                self.field_narrative(
                    get_child_attr(indicator, 'resultindicatortitle'),
                    'result_indicator_title_narrative'
                )
                self.field_narrative(
                    get_child_attr(indicator, 'resultindicatordescription'),
                    'result_indicator_description_narrative'
                )

                self.document_link(
                    indicator.result_indicator_document_links.all(),
                    prefix='result_indicator_document_link'
                )
                self.reference(
                    indicator.resultindicatorreference_set.all(),
                    prefix='result_indicator_reference',
                    is_indicator=True
                )

    def result(self):
        self.add_field('iati_identifier', self.record.activity.iati_identifier)
        self.add_field('humanitarian', bool_string(get_child_attr(self.record, 'activity.humanitarian')))

        add_reporting_org(self, self.record.activity)

        self.title()
        self.description()

        self.document_link(self.record.documentlink_set.all())
        self.reference(self.record.resultreference_set.all())

        self.indicator()

    def to_representation(self, result):
        self.record = result

        self.indexing = {}
        self.representation = {}

        self.result()
        self.build()

        return self.representation
