from solr.indexing import BaseIndexing
from solr.utils import add_reporting_org, decimal_string, value_string


class BudgetIndexing(BaseIndexing):

    def budget(self):
        budget = self.record

        self.add_field('id', budget.id)
        self.add_field('iati_identifier', budget.activity.iati_identifier)

        self.add_field('budget_type', budget.type_id)
        self.add_field('budget_status', budget.status_id)

        self.add_field('budget_period_start_iso_date', value_string(budget.period_start))
        self.add_field('budget_period_end_iso_date', value_string(budget.period_end))

        self.add_field('budget_value_currency', budget.currency_id)
        self.add_field('budget_value_date', value_string(budget.value_date))
        self.add_field('budget_value', decimal_string(budget.value))

        add_reporting_org(self, budget.activity)

    def to_representation(self, budget):
        self.record = budget
        self.indexing = {}
        self.representation = {}

        self.budget()
        self.build()

        return self.representation
