from rest_framework import serializers

from api.codelist.serializers import (
    CodelistSerializer, OrganisationNarrativeContainerSerializer,
    OrganisationNarrativeSerializer
)
from api.country.serializers import CountrySerializer
from api.fields import EncodedHyperlinkedIdentityField
from api.generics.fields import BoolToNumField
from api.generics.serializers import (
    DynamicFieldsModelSerializer, DynamicFieldsSerializer,
    ModelSerializerNoValidation, SerializerNoValidation
)
from api.generics.utils import get_or_none, get_or_raise, handle_errors
from api.region.serializers import BasicRegionSerializer
from iati.models import Narrative
from iati.parser.exceptions import ValidationError
from iati_organisation import models as org_models
from iati_organisation.parser import validators


def save_narratives(instance, data, organisation_instance):
    current_narratives = instance.narratives.all()

    current_ids = set([i.id for i in current_narratives])
    old_ids = set(filter(lambda x: x is not None, [i.get('id') for i in data]))
    new_data = filter(lambda x: x.get('id') is None, data)

    to_remove = list(current_ids.difference(old_ids))
    to_add = new_data
    to_update = list(current_ids.intersection(old_ids))

    for fk_id in to_update:
        narrative = Narrative.objects.get(pk=fk_id)
        narrative_data = filter(lambda x: x['id'] is fk_id, data)[0]

        for field, data in narrative_data.items():
            setattr(narrative, field, data)
        narrative.save()

    for fk_id in to_remove:
        narrative = Narrative.objects.get(pk=fk_id)
        narrative.delete()

    for narrative_data in to_add:

        org_models.OrganisationNarrative.objects.create(
            related_object=instance,
            organisation=organisation_instance,
            **narrative_data)


class ValueSerializer(SerializerNoValidation):
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


class OrganisationNameSerializer(SerializerNoValidation):
    narratives = OrganisationNarrativeSerializer(many=True)

    class Meta:
        model = org_models.OrganisationName
        fields = ('narratives',)


class TotalBudgetBudgetLineSerializer(ModelSerializerNoValidation):
    ref = serializers.CharField()
    value = ValueSerializer(source='*')
    narratives = OrganisationNarrativeSerializer(many=True)

    total_budget = serializers.CharField(write_only=True)

    class Meta:
        model = org_models.TotalBudgetLine
        fields = (
            'total_budget',
            'id',
            'ref',
            'value',
            'narratives',
        )

    def validate(self, data):
        total_budget = get_or_raise(
            org_models.TotalBudget, data, 'total_budget')

        validated = validators.organisation_total_budget_line(
            total_budget,
            data.get('ref'),
            data.get('value'),
            data.get('currency').get('code'),
            data.get('value_date'),
            data.get('narratives'),

        )

        return handle_errors(validated)

    def create(self, validated_data):
        total_budget = validated_data.get('total_budget')
        narratives_data = validated_data.pop('narratives', [])

        instance = org_models.TotalBudgetLine.objects.create(**validated_data)

        total_budget.organisation.modified = True
        total_budget.organisation.save()

        save_narratives(total_budget, narratives_data,
                        total_budget.organisation)

        return instance

    def update(self, instance, validated_data):
        total_budget = validated_data.get('total_budget')
        narratives_data = validated_data.pop('narratives', [])

        update_instance = org_models.TotalBudgetLine(**validated_data)
        update_instance.id = instance.id
        update_instance.save()

        total_budget.organisation.modified = True
        total_budget.organisation.save()

        save_narratives(total_budget, narratives_data,
                        total_budget.organisation)

        return update_instance


class OrganisationTotalBudgetSerializer(ModelSerializerNoValidation):

    organisation = serializers.CharField(write_only=True)

    value = ValueSerializer(source='*')
    status = CodelistSerializer()

    # because we want to validate in the validator instead
    period_start = serializers.CharField()
    period_end = serializers.CharField()

    budget_lines = TotalBudgetBudgetLineSerializer(
        many=True, source="totalbudgetline_set", required=False)

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
            'budget_lines',
        )

    def validate(self, data):
        organisation = get_or_raise(
            org_models.Organisation, data, 'organisation')

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


class RecipientOrgBudgetLineSerializer(ModelSerializerNoValidation):
    ref = serializers.CharField()
    value = ValueSerializer(source='*')
    narratives = OrganisationNarrativeSerializer(many=True)

    recipient_org_budget = serializers.CharField(write_only=True)

    class Meta:
        model = org_models.RecipientOrgBudgetLine
        fields = (
            'recipient_org_budget',
            'id',
            'ref',
            'value',
            'narratives',
        )

    def validate(self, data):
        recipient_org_budget = get_or_raise(
            org_models.RecipientOrgBudget, data, 'recipient_org_budget')

        validated = validators.organisation_recipient_org_budget_line(
            recipient_org_budget,
            data.get('ref'),
            data.get('value'),
            data.get('currency').get('code'),
            data.get('value_date'),
            data.get('narratives'),

        )

        return handle_errors(validated)

    def create(self, validated_data):
        recipient_org_budget = validated_data.get('recipient_org_budget')
        narratives_data = validated_data.pop('narratives', [])

        instance = org_models.RecipientOrgBudgetLine.objects.create(
            **validated_data)

        recipient_org_budget.organisation.modified = True
        recipient_org_budget.organisation.save()

        save_narratives(recipient_org_budget, narratives_data,
                        recipient_org_budget.organisation)

        return instance

    def update(self, instance, validated_data):
        recipient_org_budget = validated_data.get('recipient_org_budget')
        narratives_data = validated_data.pop('narratives', [])

        update_instance = org_models.RecipientOrgBudgetLine(**validated_data)
        update_instance.id = instance.id
        update_instance.save()

        recipient_org_budget.organisation.modified = True
        recipient_org_budget.organisation.save()

        save_narratives(recipient_org_budget, narratives_data,
                        recipient_org_budget.organisation)

        return update_instance


class OrganisationRecipientOrgBudgetSerializer(ModelSerializerNoValidation):
    class RecipientOrganisationSerializer(SerializerNoValidation):
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

    budget_lines = RecipientOrgBudgetLineSerializer(
        many=True, source="recipientorgbudgetline_set", required=False)

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
        organisation = get_or_raise(
            org_models.Organisation, data, 'organisation')

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

        instance = org_models.RecipientOrgBudget.objects.create(
            **validated_data)

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


class RecipientCountryBudgetLineSerializer(ModelSerializerNoValidation):
    ref = serializers.CharField()
    value = ValueSerializer(source='*')
    narratives = OrganisationNarrativeSerializer(many=True)

    recipient_country_budget = serializers.CharField(write_only=True)

    class Meta:
        model = org_models.RecipientCountryBudgetLine
        fields = (
            'recipient_country_budget',
            'id',
            'ref',
            'value',
            'narratives',
        )

    def validate(self, data):
        recipient_country_budget = get_or_raise(
            org_models.RecipientCountryBudget,
            data,
            'recipient_country_budget'
        )

        validated = validators.organisation_recipient_country_budget_line(
            recipient_country_budget,
            data.get('ref'),
            data.get('value'),
            data.get('currency').get('code'),
            data.get('value_date'),
            data.get('narratives'),

        )

        return handle_errors(validated)

    def create(self, validated_data):
        recipient_country_budget = validated_data.get(
            'recipient_country_budget')
        narratives_data = validated_data.pop('narratives', [])

        instance = org_models.RecipientCountryBudgetLine.objects.create(
            **validated_data)

        recipient_country_budget.organisation.modified = True
        recipient_country_budget.organisation.save()

        save_narratives(
            recipient_country_budget,
            narratives_data,
            recipient_country_budget.organisation)

        return instance

    def update(self, instance, validated_data):
        recipient_country_budget = validated_data.get(
            'recipient_country_budget')
        narratives_data = validated_data.pop('narratives', [])

        update_instance = org_models.RecipientCountryBudgetLine(
            **validated_data)
        update_instance.id = instance.id
        update_instance.save()

        recipient_country_budget.organisation.modified = True
        recipient_country_budget.organisation.save()

        save_narratives(
            recipient_country_budget,
            narratives_data,
            recipient_country_budget.organisation)

        return update_instance


class OrganisationRecipientCountryBudgetSerializer(
        ModelSerializerNoValidation):
    organisation = serializers.CharField(write_only=True)

    value = ValueSerializer(source='*')
    status = CodelistSerializer()

    # because we want to validate in the validator instead
    period_start = serializers.CharField()
    period_end = serializers.CharField()

    recipient_country = CountrySerializer(
        source="country", fields=('url', 'code', 'name'))

    budget_lines = RecipientCountryBudgetLineSerializer(
        many=True, source="recipientcountrybudgetline_set", required=False)

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
        organisation = get_or_raise(
            org_models.Organisation, data, 'organisation')

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

        instance = org_models.RecipientCountryBudget.objects.create(
            **validated_data)

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


class RecipientRegionBudgetLineSerializer(ModelSerializerNoValidation):
    ref = serializers.CharField()
    value = ValueSerializer(source='*')
    narratives = OrganisationNarrativeSerializer(many=True)

    recipient_region_budget = serializers.CharField(write_only=True)

    class Meta:
        model = org_models.RecipientRegionBudgetLine
        fields = (
            'recipient_region_budget',
            'id',
            'ref',
            'value',
            'narratives',
        )

    def validate(self, data):
        recipient_region_budget = get_or_raise(
            org_models.RecipientRegionBudget, data, 'recipient_region_budget')

        validated = validators.organisation_recipient_region_budget_line(
            recipient_region_budget,
            data.get('ref'),
            data.get('value'),
            data.get('currency').get('code'),
            data.get('value_date'),
            data.get('narratives'),

        )

        return handle_errors(validated)

    def create(self, validated_data):
        recipient_region_budget = validated_data.get('recipient_region_budget')
        narratives_data = validated_data.pop('narratives', [])

        instance = org_models.RecipientRegionBudgetLine.objects.create(
            **validated_data)

        recipient_region_budget.organisation.modified = True
        recipient_region_budget.organisation.save()

        save_narratives(
            recipient_region_budget,
            narratives_data,
            recipient_region_budget.organisation)

        return instance

    def update(self, instance, validated_data):
        recipient_region_budget = validated_data.get('recipient_region_budget')
        narratives_data = validated_data.pop('narratives', [])

        update_instance = org_models.RecipientRegionBudgetLine(
            **validated_data)
        update_instance.id = instance.id
        update_instance.save()

        recipient_region_budget.organisation.modified = True
        recipient_region_budget.organisation.save()

        save_narratives(
            recipient_region_budget,
            narratives_data,
            recipient_region_budget.organisation)

        return update_instance


class OrganisationRecipientRegionBudgetSerializer(ModelSerializerNoValidation):
    organisation = serializers.CharField(write_only=True)

    value = ValueSerializer(source='*')
    status = CodelistSerializer()

    # because we want to validate in the validator instead
    period_start = serializers.CharField()
    period_end = serializers.CharField()

    recipient_region = BasicRegionSerializer(
        source="region", fields=('url', 'code', 'name'))

    budget_lines = RecipientRegionBudgetLineSerializer(
        many=True, source="recipientregionbudgetline_set", required=False)

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
        organisation = get_or_raise(
            org_models.Organisation, data, 'organisation')

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

        instance = org_models.RecipientRegionBudget.objects.create(
            **validated_data)

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


class TotalExpenditureLineSerializer(ModelSerializerNoValidation):
    ref = serializers.CharField()
    value = ValueSerializer(source='*')
    narratives = OrganisationNarrativeSerializer(many=True)

    total_expenditure = serializers.CharField(write_only=True)

    class Meta:
        model = org_models.TotalExpenditureLine
        fields = (
            'total_expenditure',
            'id',
            'ref',
            'value',
            'narratives',
        )

    def validate(self, data):
        total_expenditure = get_or_raise(
            org_models.TotalExpenditure, data, 'total_expenditure')

        validated = validators.organisation_total_expenditure_line(
            total_expenditure,
            data.get('ref'),
            data.get('value'),
            data.get('currency').get('code'),
            data.get('value_date'),
            data.get('narratives'),
        )

        return handle_errors(validated)

    def create(self, validated_data):
        total_expenditure = validated_data.get('total_expenditure')
        narratives_data = validated_data.pop('narratives', [])

        instance = org_models.TotalExpenditureLine.objects.create(
            **validated_data)

        total_expenditure.organisation.modified = True
        total_expenditure.organisation.save()

        save_narratives(total_expenditure, narratives_data,
                        total_expenditure.organisation)

        return instance

    def update(self, instance, validated_data):
        total_expenditure = validated_data.get('total_expenditure')
        narratives_data = validated_data.pop('narratives', [])

        update_instance = org_models.TotalExpenditureLine(**validated_data)
        update_instance.id = instance.id
        update_instance.save()

        total_expenditure.organisation.modified = True
        total_expenditure.organisation.save()

        save_narratives(total_expenditure, narratives_data,
                        total_expenditure.organisation)

        return update_instance


class OrganisationTotalExpenditureSerializer(ModelSerializerNoValidation):
    organisation = serializers.CharField(write_only=True)

    value = ValueSerializer(source='*')

    # because we want to validate in the validator instead
    period_start = serializers.CharField()
    period_end = serializers.CharField()

    expense_line = TotalExpenditureLineSerializer(
        many=True, source="totalexpenditureline_set", required=False)

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
        organisation = get_or_raise(
            org_models.Organisation, data, 'organisation')

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


class OrganisationDocumentLinkCategorySerializer(ModelSerializerNoValidation):
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
        document_link = get_or_raise(
            org_models.OrganisationDocumentLink, data, 'document_link')

        validated = validators.document_link_category(
            document_link,
            data.get('category', {}).get('code'),
        )

        return handle_errors(validated)

    def create(self, validated_data):
        document_link = validated_data.get('document_link')

        instance = org_models.OrganisationDocumentLinkCategory.objects.create(
            **validated_data)

        document_link.organisation.modified = True
        document_link.organisation.save()

        return instance

    def update(self, instance, validated_data):
        document_link = validated_data.get('document_link')

        update_instance = org_models.OrganisationDocumentLinkCategory(
            **validated_data)
        update_instance.id = instance.id
        update_instance.save()

        document_link.organisation.modified = True
        document_link.organisation.save()

        return update_instance


class OrganisationDocumentLinkLanguageSerializer(ModelSerializerNoValidation):
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
        document_link = get_or_raise(
            org_models.OrganisationDocumentLink, data, 'document_link')

        validated = validators.document_link_language(
            document_link,
            data.get('language', {}).get('code'),
        )

        return handle_errors(validated)

    def create(self, validated_data):
        document_link = validated_data.get('document_link')

        instance = org_models.OrganisationDocumentLinkLanguage.objects.create(
            **validated_data)

        document_link.organisation.modified = True
        document_link.organisation.save()

        return instance

    def update(self, instance, validated_data):
        document_link = validated_data.get('document_link')

        update_instance = org_models.OrganisationDocumentLinkLanguage(
            **validated_data)
        update_instance.id = instance.id
        update_instance.save()

        document_link.organisation.modified = True
        document_link.organisation.save()

        return update_instance


class OrganisationDocumentLinkRecipientCountrySerializer(
        ModelSerializerNoValidation):
    recipient_country = CodelistSerializer()

    document_link = serializers.CharField(write_only=True)

    budget_lines = RecipientCountryBudgetLineSerializer(
        many=True, source="recipientcountrybudgetline_set", required=False)

    class Meta:
        model = org_models.DocumentLinkRecipientCountry
        fields = (
            'document_link',
            'id',
            'recipient_country',
            'budget_lines',
        )

    def validate(self, data):
        document_link = get_or_raise(
            org_models.OrganisationDocumentLink, data, 'document_link')

        validated = validators.document_link_recipient_country(
            document_link,
            data.get('recipient_country', {}).get('code'),
        )

        return handle_errors(validated)

    def create(self, validated_data):
        document_link = validated_data.get('document_link')

        instance = org_models.DocumentLinkRecipientCountry.objects.create(
            **validated_data)

        document_link.organisation.modified = True
        document_link.organisation.save()

        return instance

    def update(self, instance, validated_data):
        document_link = validated_data.get('document_link')

        update_instance = org_models.DocumentLinkRecipientCountry(
            **validated_data)
        update_instance.id = instance.id
        update_instance.save()

        document_link.organisation.modified = True
        document_link.organisation.save()

        return update_instance


class OrganisationDocumentLinkSerializer(ModelSerializerNoValidation):

    class DocumentDateSerializer(SerializerNoValidation):
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

    title = OrganisationNarrativeContainerSerializer(
        source="documentlinktitle")

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
        organisation = get_or_raise(
            org_models.Organisation, data, 'organisation')

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

        instance = org_models.OrganisationDocumentLink.objects.create(
            **validated_data)

        document_link_title = org_models.DocumentLinkTitle.objects.create(
            document_link=instance)

        save_narratives(document_link_title,
                        title_narratives_data, organisation)

        organisation.modified = True
        organisation.save()

        return instance

    def update(self, instance, validated_data):
        organisation = validated_data.get('organisation')
        title_narratives_data = validated_data.pop('title_narratives', [])

        update_instance = org_models.OrganisationDocumentLink(**validated_data)
        update_instance.id = instance.id
        update_instance.save()

        save_narratives(update_instance.documentlinktitle,
                        title_narratives_data, organisation)

        organisation.modified = True
        organisation.save()

        return update_instance


class OrganisationReportingOrganisationSerializer(ModelSerializerNoValidation):
    xml_meta = {'attributes': ('ref', 'type', 'secondary_reporter')}

    ref = serializers.CharField(source="reporting_org_identifier")
    type = CodelistSerializer(source="org_type")
    secondary_reporter = BoolToNumField()

    narratives = OrganisationNarrativeSerializer(many=True)

    class Meta:
        model = org_models.OrganisationReportingOrganisation
        fields = (
            'ref',
            'type',
            'secondary_reporter',
            'narratives',
        )


class OrganisationSerializer(DynamicFieldsModelSerializer):
    class PublishedStateSerializer(DynamicFieldsSerializer):
        published = serializers.BooleanField()
        ready_to_publish = serializers.BooleanField()
        modified = serializers.BooleanField()

    url = EncodedHyperlinkedIdentityField(
        view_name='organisations:organisation-detail', read_only=True)

    last_updated_datetime = serializers.DateTimeField(required=False)
    xml_lang = serializers.CharField(
        source='default_lang.code', required=False)
    default_currency = CodelistSerializer(required=False)
    name = OrganisationNameSerializer(required=False)

    published_state = PublishedStateSerializer(source="*", read_only=True)

    reporting_org = OrganisationReportingOrganisationSerializer(read_only=True)
    total_budgets = OrganisationTotalBudgetSerializer(
        many=True,
        read_only=True
    )
    recipient_org_budgets = OrganisationRecipientOrgBudgetSerializer(
        source='recipientorgbudget_set',
        many=True,
        read_only=True
    )

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
            'reporting_org',
            'total_budgets',
            'recipient_org_budgets',
            'published_state',
            'primary_name',
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
        old_organisation = get_or_none(
            org_models.Organisation,
            validated_data,
            'organisation_identifier')

        if old_organisation:
            raise ValidationError({
                "organisation_identifier":
                "Organisation with this IATI identifier already exists"
            })

        name_data = validated_data.pop('name', None)  # NOQA: F841
        name_narratives_data = validated_data.pop('name_narratives', None)

        # TODO: only allow user to create the organisation he is
        # validated with on the IATI registry - 2017-03-06

        instance = org_models.Organisation.objects.create(**validated_data)
        instance.publisher_id = self.context['view'].kwargs.get('publisher_id')
        instance.published = False
        instance.ready_to_publish = False
        instance.modified = True

        instance.save()

        name = org_models.OrganisationName.objects.create(
            organisation=instance)
        instance.name = name

        if name_narratives_data:
            save_narratives(name, name_narratives_data, instance)

        return instance

    def update(self, instance, validated_data):
        name_data = validated_data.pop('name', None)  # NOQA: F841
        name_narratives_data = validated_data.pop('name_narratives', None)

        update_instance = org_models.Organisation(**validated_data)
        update_instance.id = instance.id
        update_instance.modified = True
        update_instance.save()

        if name_narratives_data:
            save_narratives(update_instance.name,
                            name_narratives_data, instance)

        return update_instance
