from rest_framework import serializers
from rest_framework.renderers import JSONRenderer

from api.activity.serializers import NarrativeSerializer
from solr.utils import add_dict, add_value_list


class BaseIndexing(serializers.Serializer):
    representation = {}
    indexing = {}
    record = None

    def set_field(self, field, value):
        add_dict(self.representation, field, value)

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
                    value = JSONRenderer().render(NarrativeSerializer(narrative).data).decode() if is_json_string else NarrativeSerializer(narrative).data  # NOQA: E501
                    add_value_list(narratives, value)

                self.set_field(field_name, narratives)

    def related_narrative(
            self,
            related,
            narrative_key,
            narrative_text_key,
            narrative_lang_key
    ):
        if related:
            for narrative in related.narratives.all():
                self.add_value_list(narrative_key, narrative.content)
                self.add_value_list(narrative_text_key, narrative.content)

                if narrative.language:
                    self.add_value_list(
                        narrative_lang_key,
                        narrative.language.code
                    )
