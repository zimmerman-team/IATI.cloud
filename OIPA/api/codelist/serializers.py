from rest_framework import serializers
from iati.models import Narrative, DocumentCategory
from iati_synchroniser.models import Codelist
from api.generics.serializers import DynamicFieldsSerializer, DynamicFieldsModelSerializer
from django.core.urlresolvers import reverse


class VocabularySerializer(serializers.Serializer):
    code = serializers.CharField(required=False, allow_null=True)
    name = serializers.CharField(required=False, allow_null=True)


class CodelistSerializer(DynamicFieldsSerializer):
    code = serializers.CharField(required=False, allow_null=True)
    name = serializers.CharField(required=False, allow_null=True)


class CodelistCategorySerializer(CodelistSerializer):
    category = CodelistSerializer(required=False, allow_null=True)


class CodelistVocabularySerializer(CodelistSerializer):
    vocabulary = VocabularySerializer(required=False, allow_null=True)


class NarrativeSerializer(serializers.ModelSerializer):
    text = serializers.CharField(source="content")
    language = CodelistSerializer(required=False)

    class Meta:
        model = Narrative
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
        model = DocumentCategory
        fields = ('code', 'name')


class CodelistItemSerializer(DynamicFieldsModelSerializer):
    code = serializers.CharField()
    name = serializers.CharField(required=False)
    vocabulary = VocabularySerializer(required=False)
    category = CodelistSerializer(required=False)

    class Meta:
        model = None
        fields = ('code', 'name', 'vocabulary', 'category')


class CodelistMetaSerializer(DynamicFieldsModelSerializer):
    name = serializers.CharField()
    items = serializers.SerializerMethodField()

    def get_items(self, obj):
        request = self.context.get('request')
        url = request.build_absolute_uri(reverse('codelists:codelist-items-list', kwargs={'codelist': obj.name}))
        return url

    class Meta:
        model = Codelist
        fields = ('name', 'items')
