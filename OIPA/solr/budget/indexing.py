from solr.indexing import BaseIndexing
from solr.utils import (
    add_reporting_org, bool_string, date_string, decimal_string
)


def add_recipient_country(serializer, activity):
    recipient_country_all = activity.activityrecipientcountry_set.all()
    if recipient_country_all:
        serializer.add_field('recipient_country_code', [])
        serializer.add_field('recipient_country_name', [])
        serializer.add_field('recipient_country_percentage', [])

        serializer.add_field('recipient_country_narrative', [])
        serializer.add_field('recipient_country_narrative_lang', [])
        serializer.add_field('recipient_country_narrative_text', [])

        for recipient_country in recipient_country_all:
            serializer.add_value_list(
                'recipient_country_code',
                recipient_country.country.code
            )
            serializer.add_value_list(
                'recipient_country_name',
                recipient_country.country.name
            )
            serializer.add_value_list(
                'recipient_country_percentage',
                recipient_country.percentage
            )
            serializer.related_narrative(
                recipient_country,
                'recipient_country_narrative',
                'recipient_country_narrative_lang',
                'recipient_country_narrative_text'
            )


def add_recipient_region(serializer, activity):
    recipient_region_all = activity.activityrecipientregion_set.all()
    if recipient_region_all:

        serializer.add_field('recipient_region_code', [])
        serializer.add_field('recipient_region_name', [])

        serializer.add_field('recipient_region_vocabulary', [])
        serializer.add_field('recipient_region_vocabulary_uri', [])

        serializer.add_field('recipient_region_percentage', [])

        serializer.add_field('recipient_region_narrative', [])
        serializer.add_field('recipient_region_narrative_lang', [])
        serializer.add_field('recipient_region_narrative_text', [])

        for recipient_region in recipient_region_all:
            serializer.add_value_list(
                'recipient_region_code',
                recipient_region.region.code
            )
            serializer.add_value_list(
                'recipient_region_name',
                recipient_region.region.name
            )
            if recipient_region.vocabulary.code:
                serializer.add_value_list(
                    'recipient_region_vocabulary',
                    recipient_region.vocabulary.code
                )
            else:
                serializer.indexing['recipient_region_vocabulary'].append(' ')
            if recipient_region.vocabulary_uri:
                serializer.add_value_list(
                    'recipient_region_vocabulary_uri',
                    recipient_region.vocabulary_uri
                )
            else:
                serializer.indexing['recipient_region_vocabulary_uri'].append(
                    ' ')
            serializer.add_value_list(
                'recipient_region_percentage',
                recipient_region.percentage
            )

            serializer.related_narrative(
                recipient_region,
                'recipient_region_narrative',
                'recipient_region_narrative_text',
                'recipient_region_narrative_lang'
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

        self.add_field(
            'humanitarian',
            bool_string(budget.activity.humanitarian)
        )

        add_reporting_org(self, budget.activity)
        add_recipient_country(self, budget.activity)
        add_recipient_region(self, budget.activity)

    def to_representation(self, budget):
        self.record = budget
        self.indexing = {}
        self.representation = {}

        self.budget()
        self.build()

        return self.representation
