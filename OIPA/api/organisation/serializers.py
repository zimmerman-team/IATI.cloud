from iati_organisation import models as org_models
import iati
from rest_framework import serializers
from api.generics.serializers import DynamicFieldsSerializer, DynamicFieldsModelSerializer, FilterableModelSerializer

from api.fields import EncodedHyperlinkedIdentityField

from api.codelist.serializers import OrganisationNarrativeSerializer, OrganisationNarrativeContainerSerializer
from api.codelist.serializers import VocabularySerializer
from api.codelist.serializers import CodelistSerializer
from api.codelist.serializers import CodelistCategorySerializer

from iati_organisation.parser import validators
from iati.parser import exceptions
from api.generics.utils import handle_errors
from api.generics.utils import get_or_raise, get_or_none

def save_narratives(instance, data, organisation_instance):
    current_narratives = instance.narratives.all()

    current_ids = set([ i.id for i in current_narratives ])
    old_ids = set(filter(lambda x: x is not None, [ i.get('id') for i in data ]))
    new_data = filter(lambda x: x.get('id') is None, data)

    # print(current_ids)
    # print(old_ids)
    # print(new_data)

    to_remove = list(current_ids.difference(old_ids))
    # to_add = list(new_ids.difference(current_ids))
    to_add = new_data
    to_update = list(current_ids.intersection(old_ids))

    for fk_id in to_update:
        narrative = iati_models.Narrative.objects.get(pk=fk_id)
        narrative_data = filter(lambda x: x['id'] is fk_id, data)[0]

        for field, data in narrative_data.iteritems():
            setattr(narrative, field, data)
        narrative.save()

    for fk_id in to_remove:
        narrative = iati_models.Narrative.objects.get(pk=fk_id)
        # instance = instances.get(pk=fk_id)
        narrative.delete()

    for narrative_data in to_add:
        # narrative = iati_models.Narrative.objects.get(pk=fk_id)
        # narrative_data = filter(lambda x: x['id'] is fk_id, data)[0]

        org_models.OrganisationNarrative.objects.create(
                related_object=instance, 
                organisation=organisation_instance,
                **narrative_data)

class ValueSerializer(serializers.Serializer):
    currency = CodelistSerializer()
    date = serializers.CharField(source='value_date')
    value = serializers.DecimalField(
            max_digits=15,
            decimal_places=2,
            coerce_to_string=False,
            )

    class Meta:
        fields = (
                'value',
                'date',
                'currency',
                )

class DocumentLinkSerializer(serializers.ModelSerializer):

    class DocumentCategorySerializer(serializers.ModelSerializer):

        class Meta:
            model = iati.models.DocumentCategory
            fields = ('code', 'name')

    format = CodelistSerializer(source='file_format')
    categories = DocumentCategorySerializer(many=True)
    title = OrganisationNarrativeContainerSerializer(source="documentlinktitles", many=True)

    class Meta:
        model = org_models.DocumentLink
        fields = (
            'url',
            'format',
            'categories',
            'title'
        )


class RecipientCountryBudgetLineSerializer(serializers.ModelSerializer):
    ref = serializers.CharField()
    value = ValueSerializer(source='*')
    narratives = OrganisationNarrativeSerializer(many=True)

    class Meta:
        model = org_models.RecipientOrgBudgetLine
        fields = (
            'ref',
            'value',
            'narratives',
        )

class RecipientCountryBudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = org_models.RecipientCountryBudget
        fields = ('period_start','period_end','country','currency','value','budget_lines','narratives')
    country = CodelistSerializer()
    currency = CodelistSerializer()
    budget_lines = RecipientCountryBudgetLineSerializer(many=True, source="recipientcountrybudgetline_set", required=False)
    narratives = OrganisationNarrativeSerializer(many=True)


# TODO: change to NarrativeContainer
class OrganisationNameSerializer(serializers.Serializer):
    narratives = OrganisationNarrativeSerializer(many=True)

    class Meta:
        model = org_models.OrganisationName
        fields = ('narratives',)

class OrganisationTotalBudgetSerializer(serializers.ModelSerializer):

    organisation = serializers.CharField(write_only=True)

    value = ValueSerializer(source='*')
    status = CodelistSerializer()

    # because we want to validate in the validator instead
    period_start = serializers.CharField()
    period_end = serializers.CharField()

    class Meta:
        model = org_models.TotalBudget
        # filter_class = BudgetFilter
        fields = (
            'organisation',
            'id',
            'status',
            'period_start',
            'period_end',
            'value',
        )

    def validate(self, data):
        organisation = get_or_raise(org_models.Organisation, data, 'organisation')

        validated = validators.organisation_total_budget(
            organisation,
            data.get('status', {}).get('code'),
            data.get('period_start'),
            data.get('period_end'),
            data.get('value'),
            data.get('currency').get('code'),
            data.get('value_date'),

        )

        return handle_errors(validated)

    def create(self, validated_data):
        organisation = validated_data.get('organisation')

        instance = org_models.TotalBudget.objects.create(**validated_data)

        organisation.modified = True
        organisation.save()

        return instance


    def update(self, instance, validated_data):
        organisation = validated_data.get('organisation')

        update_instance = org_models.TotalBudget(**validated_data)
        update_instance.id = instance.id
        update_instance.save()

        organisation.modified = True
        organisation.save()

        return update_instance


class RecipientOrgBudgetLineSerializer(serializers.ModelSerializer):
    ref = serializers.CharField()
    value = ValueSerializer(source='*')
    narratives = OrganisationNarrativeSerializer(many=True)

    class Meta:
        model = org_models.RecipientOrgBudgetLine
        fields = (
            'ref',
            'value',
            'narratives',
        )

class OrganisationRecipientOrgBudgetSerializer(serializers.ModelSerializer):
    class RecipientOrganisationSerializer(serializers.Serializer):
        ref = serializers.CharField(source="recipient_org_identifier")

        class Meta:
            fields = (
                'ref',
            )

    organisation = serializers.CharField(write_only=True)

    value = ValueSerializer(source='*')
    status = CodelistSerializer()

    # because we want to validate in the validator instead
    period_start = serializers.CharField()
    period_end = serializers.CharField()

    recipient_org = RecipientOrganisationSerializer(source="*")

    budget_lines = RecipientOrgBudgetLineSerializer(many=True, source="recipientorgbudgetline_set", required=False)

    class Meta:
        model = org_models.RecipientOrgBudget
        fields = (
            'organisation',
            'id',
            'status',
            'recipient_org',
            'period_start',
            'period_end',
            'value',
            'budget_lines',
        )

    def validate(self, data):
        organisation = get_or_raise(org_models.Organisation, data, 'organisation')

        validated = validators.organisation_recipient_org_budget(
            organisation,
            data.get('status', {}).get('code'),
            data.get('recipient_org_identifier'),
            data.get('period_start'),
            data.get('period_end'),
            data.get('value'),
            data.get('currency').get('code'),
            data.get('value_date'),
        )

        return handle_errors(validated)

    def create(self, validated_data):
        organisation = validated_data.get('organisation')

        instance = org_models.RecipientOrgBudget.objects.create(**validated_data)

        organisation.modified = True
        organisation.save()

        return instance


    def update(self, instance, validated_data):
        organisation = validated_data.get('organisation')

        update_instance = org_models.RecipientOrgBudget(**validated_data)
        update_instance.id = instance.id
        update_instance.save()

        organisation.modified = True
        organisation.save()

        return update_instance


class OrganisationSerializer(DynamicFieldsModelSerializer):
    class PublishedStateSerializer(DynamicFieldsSerializer):
        published = serializers.BooleanField()
        ready_to_publish = serializers.BooleanField()
        modified = serializers.BooleanField()

    url = EncodedHyperlinkedIdentityField(view_name='organisations:organisation-detail', read_only=True)

    id = serializers.CharField(required=False)
    organisation_identifier = serializers.CharField()
    last_updated_datetime = serializers.DateTimeField(required=False)
    xml_lang = serializers.CharField(source='default_lang.code', required=False)
    default_currency = CodelistSerializer(required=False)
    name = OrganisationNameSerializer(required=False)

    published_state = PublishedStateSerializer(source="*", read_only=True)

    class Meta:
        model = org_models.Organisation
        fields = (
            'url',
            'id',
            'organisation_identifier',
            'last_updated_datetime',
            'xml_lang',
            'default_currency',
            'name',
            'published_state',
        )

    def validate(self, data):
        validated = validators.organisation(
            data.get('organisation_identifier'),
            data.get('default_lang', {}).get('code'),
            data.get('default_currency', {}).get('code'),
            data.get('name'),
        )

        return handle_errors(validated)


    def create(self, validated_data):
        old_organisation = get_or_none(org_models.Organisation, validated_data, 'organisation_identifier')

        if old_organisation:
            raise ValidationError({
                "organisation_identifier": "Organisation with this IATI identifier already exists"
            })

        name_data = validated_data.pop('name', None)
        name_narratives_data = validated_data.pop('name_narratives', None)

        # TODO: only allow user to create the organisation he is validated with on the IATI registry - 2017-03-06

        instance = org_models.Organisation.objects.create(**validated_data)
        instance.publisher_id = self.context['view'].kwargs.get('publisher_id')
        instance.published = False
        instance.ready_to_publish = False
        instance.modified = True

        instance.save()

        name = org_models.OrganisationName.objects.create(organisation=instance)
        instance.name = name

        if name_narratives_data:
            save_narratives(name, name_narratives_data, instance)

        return instance

    def update(self, instance, validated_data):
        name_data = validated_data.pop('name', None)
        name_narratives_data = validated_data.pop('name_narratives', None)

        update_instance = org_models.Organisation(**validated_data)
        update_instance.id = instance.id
        update_instance.modified = True
        update_instance.save()

        if name_narratives_data:
            save_narratives(update_instance.name, name_narratives_data, instance)

        return update_instance

