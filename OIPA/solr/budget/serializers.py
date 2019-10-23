from solr.base import IndexingSerializer
from solr.utils import bool_string, value_string, decimal_string, get_narrative_lang_list


class BudgetSerializer(IndexingSerializer):

    def budget(self, budget):
        self.add_field('id', budget.id)
        self.add_field('iati_identifier', budget.activity.iati_identifier)

        self.add_field('budget_type', budget.type_id)
        self.add_field('budget_status', budget.status_id)

        self.add_field('budget_period_start_iso_date', value_string(budget.period_start))
        self.add_field('budget_period_end_iso_date', value_string(budget.period_end))

        self.add_field('budget_value_currency', budget.currency_id)
        self.add_field('budget_value_date', value_string(budget.value_date))
        self.add_field('budget_value', decimal_string(budget.value))

        reporting_organisation = budget.activity.reporting_organisations.first()
        if reporting_organisation:
            self.add_field('reporting_org_ref', reporting_organisation.ref)
            self.add_field('reporting_org_type', reporting_organisation.type_id)
            self.add_field('reporting_org_secondary_reporter', bool_string(reporting_organisation.secondary_reporter))
            self.add_field(
                'reporting_org_narrative',
                getattr(reporting_organisation.organisation, 'primary_name', None)
            )

    def to_representation(self, transaction):
        self.budget(transaction)
        self.build()

        return self.representation
