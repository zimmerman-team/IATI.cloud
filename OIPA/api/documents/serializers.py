from rest_framework import serializers

from iati import models as iati_models
from api.generics.serializers import DynamicFieldsModelSerializer
from api.codelist.serializers import CodelistSerializer
from api.codelist.serializers import NarrativeContainerSerializer


class DocumentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = iati_models.DocumentCategory
        fields = ('code', 'name')


class DocumentLinkSerializer(serializers.ModelSerializer):

    class DocumentDateSerializer(serializers.Serializer):
        iso_date = serializers.DateField()

    format = CodelistSerializer(source='file_format')
    categories = DocumentCategorySerializer(many=True)
    title = NarrativeContainerSerializer(source="documentlinktitle")
    document_date = DocumentDateSerializer(source="*")

    class Meta:
        model = iati_models.DocumentLink
        fields = (
            'url',
            'format',
            'categories',
            'title',
            'document_date',
        )


class DocumentSerializer(DynamicFieldsModelSerializer):
    document_link = DocumentLinkSerializer()

    class Meta:
        model = iati_models.Document
        fields = (
            'id',
            'document_name',
            'long_url',
            #'document_content',
            'document_link')
