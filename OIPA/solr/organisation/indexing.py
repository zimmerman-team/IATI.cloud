from rest_framework.renderers import JSONRenderer

from solr.indexing import BaseIndexing
from solr.utils import value_string, decimal_string, bool_string, get_narrative_lang_list, get_child_attr

from solr.organisation.serializers import OrganisationRecipientRegionBudgetSerializer, \
    OrganisationRecipientCountryBudgetSerializer
from api.organisation.serializers import OrganisationNameSerializer, OrganisationTotalBudgetSerializer, \
    OrganisationRecipientOrgBudgetSerializer, OrganisationDocumentLinkSerializer


class OrganisationIndexing(BaseIndexing):

    def document_links(self):
        document_link_all = self.record.organisationdocumentlink_set.all()
        if document_link_all:
            self.add_field('organisation_document_link', [])
            self.add_field('organisation_document_link_url', [])
            self.add_field('organisation_document_link_format', [])
            self.add_field('organisation_document_link_document_date', [])

            for document_link in document_link_all:
                self.add_value_list('organisation_document_link_url', document_link.url)
                self.add_value_list('organisation_document_link_format', document_link.file_format_id)
                self.add_value_list('organisation_document_link_document_date', value_string(document_link.iso_date))

                self.add_value_list(
                    'organisation_document_link',
                    JSONRenderer().render(OrganisationDocumentLinkSerializer(document_link).data).decode()
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

            for related_budge in related_budget_all:
                self.add_value_list(prefix + '_period_start', value_string(related_budge.period_start))
                self.add_value_list(prefix + '_period_end', value_string(related_budge.period_end))
                self.add_value_list(prefix + '_value', decimal_string(related_budge.value))
                self.add_value_list(prefix + '_value_currency', related_budge.currency_id)
                self.add_value_list(prefix + '_value_date', value_string(related_budge.value_date))

                self.add_value_list(
                    'organisation_total_budget',
                    JSONRenderer().render(serializer(related_budge).data).decode()
                )

    def name(self):
        name = get_child_attr(self.record, 'name')
        if name:
            self.add_field(
                'organisation_name',
                JSONRenderer().render(OrganisationNameSerializer(name).data).decode()
            )

            self.indexing['organisation_name_narrative_lang'], self.indexing['organisation_name_narrative'] = \
                get_narrative_lang_list(name)

    def organisation(self):
        organisation = self.record

        self.add_field('id', organisation.id)
        self.add_field('organisation_identifier', organisation.organisation_identifier)
        self.add_field('organisation_type', organisation.type_id)
        self.add_field('organisation_reported_in_iati', bool_string(organisation.reported_in_iati))
        self.add_field('organisation_published', bool_string(organisation.published))
        self.add_field('organisation_last_updated_datetime', value_string(organisation.published))
        self.add_field('organisation_default_currency_code', organisation.default_currency_id)
        self.add_field('organisation_default_lang_code', organisation.default_lang_id)

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

    def to_representation(self, organisation):
        self.record = organisation
        self.indexing = {}
        self.representation = {}

        self.organisation()
        self.build()

        return self.representation
