from collections import OrderedDict
from rest_framework import serializers

from solr.utils import add_dict, add_list


class BaseSerializer(serializers.Serializer):
    representation = OrderedDict()

    def set_field(self, field, value):
        add_dict(self.representation, field, value)


class NarrativeSerializer(BaseSerializer):

    def narrative(self, narrative):
        self.set_field('lang', narrative.language.code)
        self.set_field('text', narrative.content)

    def to_representation(self, narrative):
        self.narrative(narrative)

        return self.representation


class IndexingSerializer(BaseSerializer):
    indexing = OrderedDict()

    def add_field(self, field):
        self.indexing[field] = list()

    def add_value(self, field, value):
        add_list(self.indexing[field], value)

    def build(self):
        for key in self.indexing:
            add_dict(self.representation, key, self.indexing[key])

    def narrative(self, field, field_name='narrative'):
        if field:
            narratives_all = field.narratives.all()
            if narratives_all:
                narratives = list()
                for narrative in narratives_all:
                    add_list(narratives, NarrativeSerializer(narrative).data)

                self.set_field(field_name, narratives)
