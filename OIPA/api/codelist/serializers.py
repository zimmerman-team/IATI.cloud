from django.urls import reverse
from rest_framework import serializers

from api.generics.serializers import (
    DynamicFieldsModelSerializer, ModelSerializerNoValidation,
    SerializerNoValidation
)
from iati.models import DocumentCategory, Narrative, NameSpaceElement
from iati_codelists.models import AidType
from iati_organisation.models import OrganisationNarrative
from iati_synchroniser.models import Codelist



class VocabularySerializer(SerializerNoValidation):
    code = serializers.CharField(required=False, allow_null=True)
    name = serializers.CharField(required=False, allow_null=True)


class CodelistSerializer(SerializerNoValidation):
    code = serializers.CharField(required=False, allow_null=True)
    name = serializers.CharField(required=False, allow_null=True)


class CodelistCategorySerializer(CodelistSerializer):
    category = CodelistSerializer(required=False, allow_null=True)


class CodelistVocabularySerializer(CodelistSerializer):
    vocabulary = VocabularySerializer(required=False, allow_null=True)


class NarrativeSerializer(ModelSerializerNoValidation):
    text = serializers.CharField(source="content")
    language = CodelistSerializer(required=False)

    class Meta:
        model = Narrative
        fields = (
            'text',
            'language',
        )


class OrganisationNarrativeSerializer(ModelSerializerNoValidation):
    text = serializers.CharField(source="content")
    language = CodelistSerializer(required=False)

    class Meta:
        model = OrganisationNarrative
        fields = (
            'text',
            'language',
        )

    # def validate(self, data):
    #     print('called validate...')


class NarrativeContainerSerializer(SerializerNoValidation):
    narratives = NarrativeSerializer(many=True)
    name_space = serializers.SerializerMethodField(required=False)

    def get_name_space(self, obj):
        try:
            name_space = NameSpaceElement.objects.filter(
                parent_element_id=obj.pk).filter(
                parent_element_name=obj.__class__.__name__)
            from api.activity.serializers import NameSpaceSerializer
            namespace_serializer = NameSpaceSerializer(name_space, many=True)
        except NameSpaceElement.DoesNotExist:
            return None
            pass
        return namespace_serializer.data


class OrganisationNarrativeContainerSerializer(SerializerNoValidation):
    narratives = OrganisationNarrativeSerializer(many=True)


class DocumentCategorySerializer(ModelSerializerNoValidation):
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
        url = request.build_absolute_uri(
            reverse(
                'codelists:codelist-items-list',
                kwargs={
                    'codelist': obj.name}))
        return url

    class Meta:
        model = Codelist
        fields = ('name', 'items')


class AidTypeSerializer(serializers.ModelSerializer):
    code = serializers.CharField(required=False, allow_null=True)
    name = serializers.CharField(required=False, allow_null=True)
    vocabulary = VocabularySerializer()

    class Meta:
        model = AidType
        fields = (
            'code',
            'name',
            'vocabulary'
        )
