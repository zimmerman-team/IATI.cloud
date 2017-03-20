from iati_organisation import models as org_models
import iati
from rest_framework import serializers
from api.generics.serializers import DynamicFieldsSerializer, DynamicFieldsModelSerializer, FilterableModelSerializer

from api.fields import EncodedHyperlinkedIdentityField

from api.codelist.serializers import OrganisationNarrativeSerializer, OrganisationNarrativeContainerSerializer
from api.codelist.serializers import VocabularySerializer
from api.codelist.serializers import CodelistSerializer
from api.codelist.serializers import CodelistCategorySerializer
from api.country.serializers import CountrySerializer
from api.region.serializers import RegionSerializer, BasicRegionSerializer

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


class RecipientCountryBudgetLineSerializer(serializers.ModelSerializer):
    ref = serializers.CharField()
    value = ValueSerializer(source='*')
    narratives = OrganisationNarrativeSerializer(many=True)

    class Meta:
        model = org_models.RecipientCountryBudgetLine
        fields = (
            'ref',
            'value',
            'narratives',
        )

class OrganisationRecipientCountryBudgetSerializer(serializers.ModelSerializer):
    organisation = serializers.CharField(write_only=True)

    value = ValueSerializer(source='*')
    status = CodelistSerializer()

    # because we want to validate in the validator instead
    period_start = serializers.CharField()
    period_end = serializers.CharField()

    recipient_country = CountrySerializer(source="country", fields=('url', 'code', 'name'))

    budget_lines = RecipientCountryBudgetLineSerializer(many=True, source="recipientcountrybudgetline_set", required=False)

    class Meta:
        model = org_models.RecipientCountryBudget
        fields = (
            'organisation',
            'id',
            'status',
            'recipient_country',
            'period_start',
            'period_end',
            'value',
            'budget_lines',
        )

    def validate(self, data):
        organisation = get_or_raise(org_models.Organisation, data, 'organisation')

        validated = validators.organisation_recipient_country_budget(
            organisation,
            data.get('status', {}).get('code'),
            data.get('country', {}).get('code'),
            data.get('period_start'),
            data.get('period_end'),
            data.get('value'),
            data.get('currency').get('code'),
            data.get('value_date'),
        )

        return handle_errors(validated)

    def create(self, validated_data):
        organisation = validated_data.get('organisation')

        instance = org_models.RecipientCountryBudget.objects.create(**validated_data)

        organisation.modified = True
        organisation.save()

        return instance


    def update(self, instance, validated_data):
        organisation = validated_data.get('organisation')

        update_instance = org_models.RecipientCountryBudget(**validated_data)
        update_instance.id = instance.id
        update_instance.save()

        organisation.modified = True
        organisation.save()

        return update_instance

class RecipientRegionBudgetLineSerializer(serializers.ModelSerializer):
    ref = serializers.CharField()
    value = ValueSerializer(source='*')
    narratives = OrganisationNarrativeSerializer(many=True)

    class Meta:
        model = org_models.RecipientRegionBudgetLine
        fields = (
            'ref',
            'value',
            'narratives',
        )

class OrganisationRecipientRegionBudgetSerializer(serializers.ModelSerializer):
    organisation = serializers.CharField(write_only=True)

    value = ValueSerializer(source='*')
    status = CodelistSerializer()

    # because we want to validate in the validator instead
    period_start = serializers.CharField()
    period_end = serializers.CharField()

    recipient_region = BasicRegionSerializer(source="region", fields=('url', 'code', 'name'))

    budget_lines = RecipientRegionBudgetLineSerializer(many=True, source="recipientregionbudgetline_set", required=False)

    class Meta:
        model = org_models.RecipientRegionBudget
        fields = (
            'organisation',
            'id',
            'status',
            'recipient_region',
            'period_start',
            'period_end',
            'value',
            'budget_lines',
        )

    def validate(self, data):
        organisation = get_or_raise(org_models.Organisation, data, 'organisation')

        validated = validators.organisation_recipient_region_budget(
            organisation,
            data.get('status', {}).get('code'),
            data.get('region', {}).get('code'),
            data.get('period_start'),
            data.get('period_end'),
            data.get('value'),
            data.get('currency').get('code'),
            data.get('value_date'),
        )

        return handle_errors(validated)

    def create(self, validated_data):
        organisation = validated_data.get('organisation')

        instance = org_models.RecipientRegionBudget.objects.create(**validated_data)

        organisation.modified = True
        organisation.save()

        return instance


    def update(self, instance, validated_data):
        organisation = validated_data.get('organisation')

        update_instance = org_models.RecipientRegionBudget(**validated_data)
        update_instance.id = instance.id
        update_instance.save()

        organisation.modified = True
        organisation.save()

        return update_instance

class TotalExpenditureLineSerializer(serializers.ModelSerializer):
    ref = serializers.CharField()
    value = ValueSerializer(source='*')
    narratives = OrganisationNarrativeSerializer(many=True)

    class Meta:
        model = org_models.TotalExpenditureLine
        fields = (
            'ref',
            'value',
            'narratives',
        )

class OrganisationTotalExpenditureSerializer(serializers.ModelSerializer):
    organisation = serializers.CharField(write_only=True)

    value = ValueSerializer(source='*')

    # because we want to validate in the validator instead
    period_start = serializers.CharField()
    period_end = serializers.CharField()

    expense_line = TotalExpenditureLineSerializer(many=True, source="totalexpenditureline_set", required=False)

    class Meta:
        model = org_models.TotalExpenditure
        fields = (
            'organisation',
            'id',
            'period_start',
            'period_end',
            'value',
            'expense_line',
        )

    def validate(self, data):
        organisation = get_or_raise(org_models.Organisation, data, 'organisation')

        validated = validators.organisation_total_expenditure(
            organisation,
            data.get('period_start'),
            data.get('period_end'),
            data.get('value'),
            data.get('currency').get('code'),
            data.get('value_date'),
        )

        return handle_errors(validated)

    def create(self, validated_data):
        organisation = validated_data.get('organisation')

        instance = org_models.TotalExpenditure.objects.create(**validated_data)

        organisation.modified = True
        organisation.save()

        return instance


    def update(self, instance, validated_data):
        organisation = validated_data.get('organisation')

        update_instance = org_models.TotalExpenditure(**validated_data)
        update_instance.id = instance.id
        update_instance.save()

        organisation.modified = True
        organisation.save()

        return update_instance



class OrganisationDocumentLinkCategorySerializer(serializers.ModelSerializer):
    category = CodelistSerializer()

    document_link = serializers.CharField(write_only=True)

    class Meta:
        model = org_models.OrganisationDocumentLinkCategory
        fields = (
            'document_link',
            'id',
            'category', 
            )

    def validate(self, data):
        document_link = get_or_raise(org_models.OrganisationDocumentLink, data, 'document_link')

        validated = validators.document_link_category(
            document_link,
            data.get('category', {}).get('code'),
        )

        return handle_errors(validated)


    def create(self, validated_data):
        document_link = validated_data.get('document_link')

        instance = org_models.OrganisationDocumentLinkCategory.objects.create(**validated_data)

        document_link.organisation.modified = True
        document_link.organisation.save()

        return instance


    def update(self, instance, validated_data):
        document_link = validated_data.get('document_link')

        update_instance = org_models.OrganisationDocumentLinkCategory(**validated_data)
        update_instance.id = instance.id
        update_instance.save()

        document_link.organisation.modified = True
        document_link.organisation.save()

        return update_instance


class OrganisationDocumentLinkLanguageSerializer(serializers.ModelSerializer):
    language = CodelistSerializer()

    document_link = serializers.CharField(write_only=True)

    class Meta:
        model = org_models.OrganisationDocumentLinkLanguage
        fields = (
            'document_link',
            'id',
            'language', 
            )

    def validate(self, data):
        document_link = get_or_raise(org_models.OrganisationDocumentLink, data, 'document_link')

        validated = validators.document_link_language(
            document_link,
            data.get('language', {}).get('code'),
        )

        return handle_errors(validated)


    def create(self, validated_data):
        document_link = validated_data.get('document_link')

        instance = org_models.OrganisationDocumentLinkLanguage.objects.create(**validated_data)

        document_link.organisation.modified = True
        document_link.organisation.save()

        return instance


    def update(self, instance, validated_data):
        document_link = validated_data.get('document_link')

        update_instance = org_models.OrganisationDocumentLinkLanguage(**validated_data)
        update_instance.id = instance.id
        update_instance.save()

        document_link.organisation.modified = True
        document_link.organisation.save()

        return update_instance

class OrganisationDocumentLinkRecipientCountrySerializer(serializers.ModelSerializer):
    recipient_country = CodelistSerializer()

    document_link = serializers.CharField(write_only=True)

    class Meta:
        model = org_models.DocumentLinkRecipientCountry
        fields = (
            'document_link',
            'id',
            'recipient_country', 
            )

    def validate(self, data):
        document_link = get_or_raise(org_models.OrganisationDocumentLink, data, 'document_link')

        validated = validators.document_link_recipient_country(
            document_link,
            data.get('recipient_country', {}).get('code'),
        )

        return handle_errors(validated)


    def create(self, validated_data):
        document_link = validated_data.get('document_link')

        instance = org_models.DocumentLinkRecipientCountry.objects.create(**validated_data)

        document_link.organisation.modified = True
        document_link.organisation.save()

        return instance


    def update(self, instance, validated_data):
        document_link = validated_data.get('document_link')

        update_instance = org_models.DocumentLinkRecipientCountry(**validated_data)
        update_instance.id = instance.id
        update_instance.save()

        document_link.organisation.modified = True
        document_link.organisation.save()

        return update_instance

class OrganisationDocumentLinkSerializer(serializers.ModelSerializer):

    class DocumentDateSerializer(serializers.Serializer):
        # CharField because we want to let the validators do the parsing
        iso_date = serializers.CharField()

    format = CodelistSerializer(source='file_format')

    categories = OrganisationDocumentLinkCategorySerializer(
            many=True,
            required=False,
            source="documentlinkcategory_set"
            )

    languages = OrganisationDocumentLinkLanguageSerializer(
            many=True,
            required=False,
            source="documentlinklanguage_set"
            )

    recipient_countries = OrganisationDocumentLinkRecipientCountrySerializer(
            many=True,
            required=False,
            source="documentlinkrecipientcountry_set"
            )

    title = OrganisationNarrativeContainerSerializer(source="documentlinktitle")

    document_date = DocumentDateSerializer(source="*")

    organisation = serializers.CharField(write_only=True)

    class Meta:
        model = org_models.OrganisationDocumentLink
        fields = (
            'organisation',
            'id',
            'url',
            'format',
            'title',
            'categories',
            'languages',
            'document_date',
            'recipient_countries',
        )

    def validate(self, data):
        organisation = get_or_raise(org_models.Organisation, data, 'organisation')

        validated = validators.organisation_document_link(
            organisation,
            data.get('url'),
            data.get('file_format', {}).get('code'),
            data.get('iso_date'),
            data.get('documentlinktitle', {}).get('narratives'),
        )

        return handle_errors(validated)


    def create(self, validated_data):
        organisation = validated_data.get('organisation')
        title_narratives_data = validated_data.pop('title_narratives', [])

        instance = org_models.OrganisationDocumentLink.objects.create(**validated_data)

        document_link_title = org_models.DocumentLinkTitle.objects.create(document_link=instance)

        save_narratives(document_link_title, title_narratives_data, organisation)

        organisation.modified = True
        organisation.save()

        return instance


    def update(self, instance, validated_data):
        organisation = validated_data.get('organisation')
        title_narratives_data = validated_data.pop('title_narratives', [])

        update_instance = org_models.OrganisationDocumentLink(**validated_data)
        update_instance.id = instance.id
        update_instance.save()

        save_narratives(update_instance.documentlinktitle, title_narratives_data, organisation)

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

