from solr.indexing import BaseIndexing
from solr.utils import add_reporting_org, bool_string, date_string, decimal_string


def add_recipient_country(serializer, activity):
    recipient_country_all = activity.activityrecipientcountry_set.all()
    if recipient_country_all:
        serializer.add_field('recipient_country_code', [])
        serializer.add_field('recipient_country_name', [])

        for recipient_country in recipient_country_all:
            serializer.add_value_list(
                'recipient_country_code',
                recipient_country.country.code
            )
            serializer.add_value_list(
                'recipient_country_name',
                recipient_country.country.name
            )


class BudgetIndexing(BaseIndexing):

    def budget(self):
        budget = self.record

        self.add_field('id', budget.id)
        self.add_field('iati_identifier', budget.activity.iati_identifier)

        self.add_field('budget_type', budget.type_id)
        self.add_field('budget_status', budget.status_id)

        self.add_field(
            'budget_period_start_iso_date',
            str(budget.period_start)
        )
        self.add_field(
            'budget_period_start_iso_date_f',
            date_string(budget.period_start)
        )
        self.add_field(
            'budget_period_end_iso_date',
            str(budget.period_end)
        )
        self.add_field(
            'budget_period_end_iso_date_f',
            date_string(budget.period_end)
        )

        self.add_field('budget_value_currency', budget.currency_id)

        self.add_field('budget_value_date', str(budget.value_date))
        self.add_field('budget_value_date_f', date_string(budget.value_date))

        self.add_field('budget_value', decimal_string(budget.value))

        self.add_field('humanitarian', bool_string(budget.activity.humanitarian))

        add_reporting_org(self, budget.activity)
        add_recipient_country(self, budget.activity)

    def to_representation(self, budget):
        self.record = budget
        self.indexing = {}
        self.representation = {}

        self.budget()
        self.build()

        return self.representation
