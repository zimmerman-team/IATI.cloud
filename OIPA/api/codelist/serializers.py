from rest_framework import serializers

import iati
from api.generics.serializers import DynamicFieldsSerializer


class VocabularySerializer(serializers.Serializer):
    code = serializers.CharField()
    name = serializers.CharField()

class CodelistSerializer(DynamicFieldsSerializer):
    code = serializers.CharField()
    name = serializers.CharField(required=False)

class CodelistCategorySerializer(CodelistSerializer):
    category = CodelistSerializer()

class CodelistVocabularySerializer(CodelistSerializer):
    vocabulary = VocabularySerializer()

class NarrativeSerializer(serializers.ModelSerializer):
    text = serializers.CharField(source="content")
    language = CodelistSerializer(required=False)

    class Meta:
        model = iati.models.Narrative
        fields = (
            'text',
            'language',
        )

    # def validate(self, data):
    #     print('called validate...')

class NarrativeContainerSerializer(serializers.Serializer):
    narratives = NarrativeSerializer(many=True)

class DocumentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = iati.models.DocumentCategory
        fields = ('code', 'name')

