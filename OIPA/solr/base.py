import json
from rest_framework import serializers

from solr.utils import add_dict, add_value_list, value_string, get_child_attr


class BaseSerializer(serializers.Serializer):
    representation = {}

    def set_field(self, field, value):
        add_dict(self.representation, field, value)


class NarrativeSerializer(BaseSerializer):

    def narrative(self, narrative):
        self.set_field('lang', narrative.language.code)
        self.set_field('text', narrative.content)

    def to_representation(self, narrative):
        self.representation = {}

        self.narrative(narrative)

        return self.representation


class IndexingSerializer(BaseSerializer):
    indexing = {}
    record = None

    def add_field(self, field, value=None):
        self.indexing[field] = value

    def add_value_list(self, field, value):
        add_value_list(self.indexing[field], value)

    def build(self):
        for key in self.indexing:
            add_dict(self.representation, key, self.indexing[key])

    def narrative(self, field, field_name='narrative', is_json_string=False):
        if field:
            narratives_all = field.narratives.all()
            if narratives_all:
                narratives = list()
                for narrative in narratives_all:
                    value = json.dumps(NarrativeSerializer(narrative).data) if is_json_string \
                        else NarrativeSerializer(narrative).data
                    add_value_list(narratives, value)

                self.set_field(field_name, narratives)


class DocumentLinkSerializer(IndexingSerializer):

    def document_link(self):
        self.set_field('url', self.record.url)
        self.set_field('format', self.record.file_format_id)
        self.set_field('document_date', value_string(self.record.iso_date))

    def field_narrative(self, related, name):
        child = get_child_attr(self.record, related)
        if child:
            self.narrative(child, name)

    def category(self):
        category_all = self.record.documentlinkcategory_set.all()
        if category_all:
            category_list = list()
            for category in category_all:
                add_value_list(category_list, category.category_id)

            self.set_field('category_code', category_list)

    def language(self):
        language_all = self.record.documentlinklanguage_set.all()
        if language_all:
            language_list = list()
            for language in language_all:
                add_value_list(language_list, language.language_id)

            self.set_field('language_code', language_list)

    def to_representation(self, document_link):
        self.record = document_link

        self.representation = {}
        self.indexing = {}

        self.document_link()
        self.field_narrative('documentlinktitle', 'title')
        self.field_narrative('documentlinkdescription', 'description')
        self.category()
        self.language()

        return self.representation


class ReferenceSerializer(IndexingSerializer):

    def reference(self):
        self.set_field('code', self.record.code)
        self.set_field('vocabulary', self.record.vocabulary_id)

        if get_child_attr(self.record, 'vocabulary_uri'):
            self.set_field('vocabulary_uri', self.record.vocabulary_uri)
        else:
            self.set_field('indicator_uri', self.record.indicator_uri)

    def to_representation(self, reference):
        self.record = reference

        self.representation = {}
        self.indexing = {}

        self.reference()

        return self.representation


