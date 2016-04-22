from iati_organisation import models as org_models
import iati
from rest_framework import serializers
from api.generics.serializers import DynamicFieldsSerializer, DynamicFieldsModelSerializer, FilterableModelSerializer

from api.fields import EncodedHyperlinkedIdentityField

class VocabularySerializer(serializers.Serializer):
    code = serializers.CharField()
    name = serializers.CharField()

class CodelistSerializer(DynamicFieldsSerializer):
    code = serializers.CharField()
    name = serializers.CharField()

class CodelistCategorySerializer(CodelistSerializer):
    category = CodelistSerializer()

class CodelistVocabularySerializer(CodelistSerializer):
    vocabulary = VocabularySerializer()

# TODO: separate this
class NarrativeSerializer(serializers.ModelSerializer):
    text = serializers.CharField(source="content")
    language = CodelistSerializer()

    class Meta:
        model = iati.models.Narrative
        fields = (
            'text',
            'language',
        )
class NarrativeContainerSerializer(serializers.Serializer):
    narratives = NarrativeSerializer(many=True)


class DocumentLinkSerializer(serializers.ModelSerializer):

    class DocumentCategorySerializer(serializers.ModelSerializer):

        class Meta:
            model = iati.models.DocumentCategory
            fields = ('code', 'name')

    format = CodelistSerializer(source='file_format')
    categories = DocumentCategorySerializer(many=True)
    title = NarrativeContainerSerializer(source="documentlinktitles", many=True)

    class Meta:
        model = org_models.DocumentLink
        fields = (
            'url',
            'format',
            'categories',
            'title'
        )

class BudgetLineSerializer(serializers.ModelSerializer):
    narratives = NarrativeSerializer(many=True)
    language = CodelistSerializer()
    currency = CodelistSerializer()

    class Meta:
        model = org_models.BudgetLine
        fields = ('value_date','currency','language','currency','value','ref','narratives')



class RecipientCountryBudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = org_models.RecipientCountryBudget
        fields = ('period_start','period_end','country','currency','value','budget_lines','narratives')
    country = CodelistSerializer()
    currency = CodelistSerializer()
    budget_lines = BudgetLineSerializer(many=True)
    narratives = NarrativeSerializer(many=True)


# TODO: change to NarrativeContainer
class OrganisationNameSerializer(serializers.Serializer):
    narratives = NarrativeSerializer(many=True)

    class Meta:
        model = org_models.OrganisationName
        fields = ('narratives',)


class OrganisationSerializer(DynamicFieldsModelSerializer):
    class TypeSerializer(serializers.ModelSerializer):
        class Meta:
            model = iati.models.OrganisationType
            fields = ('code','name')

    url = EncodedHyperlinkedIdentityField(view_name='organisations:organisation-detail')
    name = OrganisationNameSerializer()

    class Meta:
        model = org_models.Organisation
        fields = (
            'url',
            'organisation_identifier',
            'name',
            'primary_name',
            'last_updated_datetime',
            'default_currency',
            'default_lang',
        )

