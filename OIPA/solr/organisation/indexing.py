from rest_framework.renderers import JSONRenderer

from api.organisation.serializers import (
    OrganisationDocumentLinkSerializer, OrganisationNameSerializer,
    OrganisationRecipientOrgBudgetSerializer,
    OrganisationTotalBudgetSerializer, OrganisationTotalExpenditureSerializer
)
from solr.indexing import BaseIndexing
from solr.organisation.serializers import (
    OrganisationRecipientCountryBudgetSerializer,
    OrganisationRecipientRegionBudgetSerializer
)
from solr.utils import (
    bool_string, date_string, decimal_string, get_child_attr,
    get_narrative_lang_list, value_string
)


class OrganisationIndexing(BaseIndexing):

    def total_expenditure(self):
        total_expenditure_all = self.record.total_expenditure.all()
        if total_expenditure_all:
            self.add_field('organisation_total_expenditure', [])
            self.add_field('organisation_total_expenditure_period_start', [])
            self.add_field('organisation_total_expenditure_period_end', [])
            self.add_field('organisation_total_expenditure_value', [])
            self.add_field('organisation_total_expenditure_value_currency', [])
            self.add_field('organisation_total_expenditure_value_date', [])

            for total_expenditure in total_expenditure_all:
                self.add_value_list(
                    'organisation_total_expenditure_period_start',
                    date_string(total_expenditure.period_start)
                )
                self.add_value_list(
                    'organisation_total_expenditure_period_end',
                    date_string(total_expenditure.period_end)
                )
                self.add_value_list(
                    'organisation_total_expenditure_value',
                    value_string(total_expenditure.value)
                )
                self.add_value_list(
                    'organisation_total_expenditure_value_currency',
                    total_expenditure.currency_id
                )
                self.add_value_list(
                    'organisation_total_expenditure_value_date',
                    date_string(total_expenditure.value_date)
                )

                self.add_value_list(
                    'organisation_total_expenditure',
                    JSONRenderer().render(
                        OrganisationTotalExpenditureSerializer(
                            instance=total_expenditure
                        ).data
                    ).decode()
                )

    def document_links(self):
        document_link_all = self.record.organisationdocumentlink_set.all()
        if document_link_all:
            self.add_field('organisation_document_link', [])
            self.add_field('organisation_document_link_url', [])
            self.add_field('organisation_document_link_format', [])
            self.add_field('organisation_document_link_document_date', [])

            for document_link in document_link_all:
                self.add_value_list(
                    'organisation_document_link_url',
                    document_link.url
                )
                self.add_value_list(
                    'organisation_document_link_format',
                    document_link.file_format_id
                )
                self.add_value_list(
                    'organisation_document_link_document_date',
                    value_string(document_link.iso_date)
                )

                self.add_value_list(
                    'organisation_document_link',
                    JSONRenderer().render(
                        OrganisationDocumentLinkSerializer(document_link).data
                    ).decode()
                )

    def related_budget(
        self,
        related_budget_all,
        serializer,
        prefix="organisation_total_budget"
    ):
        if related_budget_all:
            self.add_field(prefix + '_period_start', [])
            self.add_field(prefix + '_period_end', [])
            self.add_field(prefix + '_value', [])
            self.add_field(prefix + '_value_currency', [])
            self.add_field(prefix + '_value_date', [])
            self.add_field(prefix, [])

            for related_budget in related_budget_all:
                self.add_value_list(
                    prefix + '_period_start',
                    value_string(related_budget.period_start)
                )
                self.add_value_list(
                    prefix + '_period_end',
                    value_string(related_budget.period_end)
                )
                self.add_value_list(
                    prefix + '_value',
                    decimal_string(related_budget.value)
                )
                self.add_value_list(
                    prefix + '_value_currency',
                    related_budget.currency_id
                )
                self.add_value_list(
                    prefix + '_value_date',
                    value_string(related_budget.value_date)
                )

                self.add_value_list(
                    prefix,
                    JSONRenderer().render(
                        serializer(related_budget).data
                    ).decode()
                )

    def name(self):
        name = get_child_attr(self.record, 'name')
        if name:
            self.add_field(
                'organisation_name',
                JSONRenderer().render(
                    OrganisationNameSerializer(name).data
                ).decode()
            )

            self.indexing[
                'organisation_name_narrative_lang'
            ], self.indexing[
                'organisation_name_narrative'
            ] = get_narrative_lang_list(name)

    def organisation(self):
        organisation = self.record

        self.add_field('id', organisation.id)
        self.add_field(
            'organisation_identifier',
            organisation.organisation_identifier
        )
        self.add_field('organisation_type', organisation.type_id)
        self.add_field(
            'organisation_reported_in_iati',
            bool_string(organisation.reported_in_iati)
        )
        self.add_field(
            'organisation_published',
            bool_string(organisation.published)
        )
        self.add_field(
            'organisation_last_updated_datetime',
            value_string(organisation.last_updated_datetime)
        )
        self.add_field(
            'organisation_default_currency_code',
            organisation.default_currency_id
        )
        self.add_field(
            'organisation_default_lang_code',
            organisation.default_lang_id
        )

        self.name()
        self.related_budget(
            self.record.total_budgets.all(),
            serializer=OrganisationTotalBudgetSerializer,
            prefix="organisation_total_budget"
        )
        self.related_budget(
            self.record.recipientorgbudget_set.all(),
            serializer=OrganisationRecipientOrgBudgetSerializer,
            prefix="organisation_recipient_org_budget"
        )
        self.related_budget(
            self.record.recipient_region_budget.all(),
            serializer=OrganisationRecipientRegionBudgetSerializer,
            prefix="organisation_recipient_region_budget"
        )
        self.related_budget(
            self.record.recipient_country_budgets.all(),
            serializer=OrganisationRecipientCountryBudgetSerializer,
            prefix="organisation_recipient_country_budget"
        )
        self.document_links()
        self.total_expenditure()

    def to_representation(self, organisation):
        self.record = organisation
        self.indexing = {}
        self.representation = {}

        self.organisation()
        self.build()

        return self.representation
