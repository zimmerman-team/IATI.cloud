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
        model = org_models.OrganisationNarrative
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

    def validate(self, data):
        validated = validators.organisation(
            data.get('organisation_identifier'),
            data.get('default_lang', {}).get('code'),
            data.get('default_currency', {}).get('code'),
        )

        return handle_errors(validated)


    def create(self, validated_data):
        old_organisation = get_or_none(org_models.Organisation, validated_data, 'organisation_identifier')

        if old_organisation:
            raise ValidationError({
                "organisation_identifier": "Organisation with this IATI identifier already exists"
            })


        # TODO: only allow user to create the organisation he is validated with on the IATI registry - 2017-03-06

        instance = iati_models.RelatedActivity.objects.create(**validated_data)

        activity.modified = True
        activity.save()

        return instance


    def update(self, instance, validated_data):
        activity = validated_data.get('current_activity')

        update_instance = iati_models.RelatedActivity(**validated_data)
        update_instance.id = instance.id
        update_instance.save()

        activity.modified = True
        activity.save()

        return update_instance

