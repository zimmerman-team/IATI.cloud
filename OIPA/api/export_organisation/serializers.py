from rest_framework import serializers
from api.generics.fields import PointIATIField
from api.generics.serializers import XMLMetaMixin
from api.generics.serializers import DynamicFieldsSerializer
from api.generics.serializers import SkipNullMixin
import api.organisation.serializers as organisation_serializers
import api.transaction.serializers as transaction_serializers
from rest_framework.serializers import ModelSerializer, Serializer
from api.generics.fields import BoolToNumField

from iati_organisation import models as org_models

from geodata.models import Region, Country

class ValueXMLSerializer(XMLMetaMixin, SkipNullMixin, serializers.Serializer):
    xml_meta = {'attributes': ('currency', 'value_date')}

    currency = serializers.CharField(source='currency.code')
    value_date = serializers.CharField()
    text = serializers.DecimalField(
            source='value',
            max_digits=15,
            decimal_places=2,
            coerce_to_string=False,
            )

    class Meta():
        fields = (
                'text',
                'value_date',
                'currency',
                )


class IsoDateXMLSerializer(XMLMetaMixin, SkipNullMixin, serializers.Serializer):
    xml_meta = {'attributes': ('iso_date',)}

    iso_date = serializers.CharField(source='*')


class CodelistXMLSerializer(XMLMetaMixin, SkipNullMixin, DynamicFieldsSerializer):
    """
    Define this from scratch to have only code field.
    """
    xml_meta = {'attributes': ('code',)}

    code = serializers.CharField()


# TODO: separate this
class OrganisationNarrativeXMLSerializer(XMLMetaMixin, SkipNullMixin, serializers.Serializer):
    xml_meta = {'attributes': ('xml_lang',)}

    text = serializers.CharField(source="content")
    xml_lang = serializers.CharField(source='language.code')

    class Meta:
        model = org_models.OrganisationNarrative
        fields = (
            'text',
            'xml_lang',
            )

class OrganisationNarrativeContainerXMLSerializer(XMLMetaMixin, SkipNullMixin, serializers.Serializer):
    narrative = OrganisationNarrativeXMLSerializer(many=True, source='narratives')


class RegionXMLSerializer(XMLMetaMixin, SkipNullMixin, ModelSerializer):
    xml_meta = {'attributes': ('vocabulary', 'vocabulary_uri', 'code')}

    vocabulary = serializers.CharField(source='vocabulary.code')
    vocabulary_uri = serializers.CharField()
    code = serializers.CharField()

    class Meta:
        model = Region
        fields = (
            'vocabulary',
            'vocabulary_uri',
            'code',
        )

class CountryXMLSerializer(XMLMetaMixin, SkipNullMixin, ModelSerializer):
    xml_meta = {'attributes': ('code', )}

    code = serializers.CharField()

    class Meta:
        model = Country
        fields = (
            'code',
        )

class TotalBudgetBudgetLineXMLSerializer(XMLMetaMixin, SkipNullMixin, ModelSerializer):
    xml_meta = {'attributes': ('ref', )}

    ref = serializers.CharField()
    value = ValueXMLSerializer(source='*')
    narratives = OrganisationNarrativeXMLSerializer(many=True)

    class Meta:
        model = org_models.TotalBudgetLine
        fields = (
            'ref',
            'value',
            'narratives',
        )


class OrganisationTotalBudgetXMLSerializer(XMLMetaMixin, SkipNullMixin, ModelSerializer):
    xml_meta = {'attributes': ('status', )}

    value = ValueXMLSerializer(source='*')
    status = serializers.CharField(source="status.code")

    period_start = serializers.CharField()
    period_end = serializers.CharField()

    budget_lines = TotalBudgetBudgetLineXMLSerializer(many=True, source="totalbudgetline_set")

    class Meta:
        model = org_models.TotalBudget
        # filter_class = BudgetFilter
        fields = (
            'status',
            'period_start',
            'period_end',
            'value',
            'budget_lines',
        )


class RecipientOrgBudgetLineXMLSerializer(XMLMetaMixin, SkipNullMixin, ModelSerializer):
    xml_meta = {'attributes': ('ref', )}

    ref = serializers.CharField()
    value = ValueXMLSerializer(source='*')
    narratives = OrganisationNarrativeXMLSerializer(many=True)

    class Meta:
        model = org_models.RecipientOrgBudgetLine
        fields = (
            'ref',
            'value',
            'narratives',
        )

class OrganisationRecipientOrgBudgetXMLSerializer(XMLMetaMixin, SkipNullMixin, ModelSerializer):
    xml_meta = {'attributes': ('status', )}

    class RecipientOrganisationXMLSerializer(Serializer):
        xml_meta = {'attributes': ('ref', )}
        ref = serializers.CharField(source="recipient_org_identifier")

        class Meta:
            fields = (
                'ref',
            )

    value = ValueXMLSerializer(source='*')
    status = serializers.CharField(source="status.code")

    period_start = serializers.CharField()
    period_end = serializers.CharField()

    recipient_org = RecipientOrganisationXMLSerializer(source="*")

    budget_lines = RecipientOrgBudgetLineXMLSerializer(many=True, source="recipientorgbudgetline_set")

    class Meta:
        model = org_models.RecipientOrgBudget
        fields = (
            'status',
            'recipient_org',
            'period_start',
            'period_end',
            'value',
            'budget_lines',
        )



class RecipientCountryBudgetLineXMLSerializer(XMLMetaMixin, SkipNullMixin, ModelSerializer):
    xml_meta = {'attributes': ('ref', )}

    ref = serializers.CharField()
    value = ValueXMLSerializer(source='*')
    narratives = OrganisationNarrativeXMLSerializer(many=True)

    class Meta:
        model = org_models.RecipientCountryBudgetLine
        fields = (
            'ref',
            'value',
            'narratives',
        )

class OrganisationRecipientCountryBudgetXMLSerializer(XMLMetaMixin, SkipNullMixin, ModelSerializer):
    xml_meta = {'attributes': ('status', )}

    value = ValueXMLSerializer(source='*')
    status = serializers.CharField(source="status.code")

    period_start = serializers.CharField()
    period_end = serializers.CharField()

    recipient_country = CountryXMLSerializer(source="country")

    budget_lines = RecipientCountryBudgetLineXMLSerializer(many=True, source="recipientcountrybudgetline_set")

    class Meta:
        model = org_models.RecipientCountryBudget
        fields = (
            'status',
            'recipient_country',
            'period_start',
            'period_end',
            'value',
            'budget_lines',
        )

class RecipientRegionBudgetLineXMLSerializer(XMLMetaMixin, SkipNullMixin, ModelSerializer):
    xml_meta = {'attributes': ('ref', )}

    ref = serializers.CharField()
    value = ValueXMLSerializer(source='*')
    narratives = OrganisationNarrativeXMLSerializer(many=True)

    class Meta:
        model = org_models.RecipientRegionBudgetLine
        fields = (
            'ref',
            'value',
            'narratives',
        )

class OrganisationRecipientRegionBudgetXMLSerializer(XMLMetaMixin, SkipNullMixin, ModelSerializer):
    xml_meta = {'attributes': ('status', )}

    value = ValueXMLSerializer(source='*')
    status = serializers.CharField(source="status.code")

    period_start = serializers.CharField()
    period_end = serializers.CharField()

    recipient_region = RegionXMLSerializer(source="region")

    budget_lines = RecipientRegionBudgetLineXMLSerializer(many=True, source="recipientregionbudgetline_set")

    class Meta:
        model = org_models.RecipientRegionBudget
        fields = (
            'status',
            'recipient_region',
            'period_start',
            'period_end',
            'value',
            'budget_lines',
        )


class TotalExpenditureLineXMLSerializer(XMLMetaMixin, SkipNullMixin, ModelSerializer):
    xml_meta = {'attributes': ('ref', )}

    ref = serializers.CharField()
    value = ValueXMLSerializer(source='*')
    narratives = OrganisationNarrativeXMLSerializer(many=True)

    class Meta:
        model = org_models.TotalExpenditureLine
        fields = (
            'ref',
            'value',
            'narratives',
        )

class OrganisationTotalExpenditureXMLSerializer(XMLMetaMixin, SkipNullMixin, ModelSerializer):
    value = ValueXMLSerializer(source='*')

    period_start = serializers.CharField()
    period_end = serializers.CharField()

    expense_line = TotalExpenditureLineXMLSerializer(many=True, source="totalexpenditureline_set")

    class Meta:
        model = org_models.TotalExpenditure
        fields = (
            'period_start',
            'period_end',
            'value',
            'expense_line',
        )

class DocumentLinkCategoryXMLSerializer(XMLMetaMixin, SkipNullMixin, Serializer):
    """
    Define this from scratch to have only code field.
    """
    xml_meta = {'attributes': ('code',)}

    code = serializers.CharField(source="category.code")


class DocumentLinkRecipientCountryXMLSerializer(XMLMetaMixin, SkipNullMixin, Serializer):
    """
    Define this from scratch to have only code field.
    """
    xml_meta = {'attributes': ('code',)}

    code = serializers.CharField(source="recipient_country.code")

class OrganisationDocumentLinkXMLSerializer(XMLMetaMixin, SkipNullMixin, ModelSerializer):
    xml_meta = {'attributes': ('url', 'format')}

    format = serializers.CharField(source='file_format.code')

    category = DocumentLinkCategoryXMLSerializer(
            many=True,
            source="categories"
            )

    language = CodelistXMLSerializer()

    recipient_country = DocumentLinkRecipientCountryXMLSerializer(
            many=True,
            source="recipient_countries"
            )

    title = OrganisationNarrativeContainerXMLSerializer(source="documentlinktitle")

    document_date = IsoDateXMLSerializer(source="*")

    class Meta:
        model = org_models.OrganisationDocumentLink
        fields = (
            'url',
            'format',
            'title',
            'category',
            'language',
            'document_date',
            'recipient_country',
        )

class OrganisationReportingOrganisationXMLSerializer(XMLMetaMixin, SkipNullMixin, ModelSerializer):
    xml_meta = {'attributes': ('ref', 'type', 'secondary_reporter')}

    ref = serializers.CharField(source="reporting_org_identifier")
    type = serializers.CharField(source="org_type")
    secondary_reporter = BoolToNumField()

    narrative = OrganisationNarrativeXMLSerializer(many=True, source="narratives")

    class Meta:
        model = org_models.OrganisationReportingOrganisation
        fields = (
            'ref',
            'type',
            'secondary_reporter',
            'narrative',
        )


class OrganisationXMLSerializer(XMLMetaMixin, SkipNullMixin, ModelSerializer):
    xml_meta = {'attributes': ('last_updated_datetime', 'xml_lang', 'default_currency')}

    xml_lang = serializers.CharField(source='default_lang.code')
    default_currency = serializers.CharField(source="default_currency.code")

    name = OrganisationNarrativeContainerXMLSerializer()

    reporting_org = OrganisationReportingOrganisationXMLSerializer()
    total_budget = OrganisationTotalBudgetXMLSerializer(many=True, source="total_budgets")
    recipient_org_budget = OrganisationRecipientOrgBudgetXMLSerializer(many=True, source="recipientorgbudget_set")
    recipient_region_budget = OrganisationRecipientRegionBudgetXMLSerializer(many=True)
    recipient_country_budget = OrganisationRecipientCountryBudgetXMLSerializer(many=True, source="recipient_country_budgets")
    total_expenditure = OrganisationTotalExpenditureXMLSerializer(many=True)
    document_link = OrganisationDocumentLinkXMLSerializer(many=True, source="organisationdocumentlink_set")

    class Meta:
        model = org_models.Organisation
        fields = (
            'last_updated_datetime',
            'xml_lang',
            'default_currency',
            'organisation_identifier',
            'name',
            'reporting_org',
            'total_budget',
            'recipient_org_budget',
            'recipient_region_budget',
            'recipient_country_budget',
            'total_expenditure',
            'document_link',
        )

