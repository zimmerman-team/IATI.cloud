
from rest_framework.renderers import JSONRenderer

from solr.activity.serializers import ActivitySectorSerializer
from solr.indexing import BaseIndexing
from solr.utils import (
    add_reporting_org, bool_string, date_string, decimal_string,
    get_child_attr, get_narrative_lang_list
)


class TransactionIndexing(BaseIndexing):

    def transaction(self):
        transaction = self.record

        self.add_field('id', transaction.id)
        self.add_field('iati_identifier', transaction.activity.iati_identifier)

        if get_child_attr(transaction, 'activity.title'):
            self.indexing['title_lang'], self.indexing['title_narrative'] = \
                get_narrative_lang_list(transaction.activity.title)

        self.add_field('description_type', [])
        self.add_field('description_lang', [])
        self.add_field('description_narrative', [])
        for description in transaction.activity.description_set.all():
            self.add_value_list(
                'description_type',
                description.type_id
            )
            for narrative in description.narratives.all():
                self.add_value_list(
                    'description_narrative',
                    narrative.content
                )
                self.add_value_list(
                    'description_lang',
                    narrative.language_id
                )

        self.add_field('activity_date_type', [])
        self.add_field('activity_date_iso_date', [])

        add_reporting_org(self, transaction.activity)

        self.add_field('transaction_ref', transaction.ref)
        self.add_field(
            'transaction_humanitarian',
            bool_string(transaction.humanitarian)
        )
        self.add_field('transaction_type', transaction.transaction_type_id)
        self.add_field(
            'transaction_date_iso_date',
            date_string(transaction.transaction_date)
        )
        self.add_field('transaction_value_currency', transaction.currency_id)
        self.add_field(
            'transaction_value_date',
            date_string(transaction.value_date)
        )
        self.add_field('transaction_value', decimal_string(transaction.value))

        self.add_field(
            'transaction_provider_org_provider_activity_id',
            get_child_attr(
                transaction,
                'provider_organisation.provider_activity_ref'
            )
        )
        self.add_field(
            'transaction_provider_org_type',
            get_child_attr(transaction, 'provider_organisation.type_id')
        )
        self.add_field(
            'transaction_provider_org_ref',
            get_child_attr(transaction, 'provider_organisation.ref')
        )

        provider_organisation = getattr(
            transaction,
            'provider_organisation',
            None
        )
        if provider_organisation:
            narrative = provider_organisation.narratives.first()
            if narrative:
                self.add_field(
                    'transaction_provider_org_narrative',
                    narrative.content
                )
                self.add_field(
                    'transaction_provider_org_narrative_text',
                    narrative.content
                )
                self.add_field(
                    'transaction_provider_org_narrative_lang',
                    narrative.language_id
                )

        self.add_field(
            'transaction_receiver_org_receiver_activity_id',
            get_child_attr(
                transaction,
                'receiver_organisation.receiver_activity_ref'
            )
        )
        self.add_field(
            'transaction_receiver_org_type',
            get_child_attr(transaction, 'receiver_organisation.type_id')
        )
        self.add_field(
            'transaction_receiver_org_ref',
            get_child_attr(transaction, 'receiver_organisation.ref')
        )

        self.add_field('transaction_receiver_org_narrative', [])
        self.add_field('transaction_receiver_org_narrative_lang', [])
        self.add_field('transaction_receiver_org_narrative_text', [])
        receiver_organisation = getattr(
            transaction,
            'receiver_organisation',
            None
        )
        if receiver_organisation:
            for narrative in receiver_organisation.narratives.all():
                self.add_value_list(
                    'transaction_receiver_org_narrative',
                    narrative.content
                )
                self.add_value_list(
                    'transaction_receiver_org_narrative_text',
                    narrative.content
                )
                self.add_value_list(
                    'transaction_receiver_org_narrative_lang',
                    narrative.language_id
                )

        self.add_field(
            'transaction_disburstment_channel_code',
            transaction.disbursement_channel_id
        )

        self.add_field('transaction_sector_vocabulary', [])
        self.add_field('transaction_sector_vocabulary_uri', [])
        self.add_field('transaction_sector_code', [])
        for transaction_sector in transaction.transactionsector_set.all():
            self.add_value_list(
                'transaction_sector_vocabulary',
                transaction_sector.vocabulary_id
            )
            self.add_value_list(
                'transaction_sector_vocabulary_uri',
                transaction_sector.vocabulary_uri
            )
            self.add_value_list(
                'transaction_sector_code',
                transaction_sector.sector_id
            )

        self.add_field(
            'transaction_recipient_country_code',
            get_child_attr(
                transaction,
                'transaction_recipient_country.country_id'
            )
        )
        self.add_field(
            'transaction_recipient_region_code',
            get_child_attr(
                transaction,
                'transaction_recipient_region.region_id'
            )
        )
        self.add_field(
            'transaction_recipient_region_vocabulary',
            get_child_attr(
                transaction,
                'transaction_recipient_region.vocabulary_id'
            )
        )

        self.add_field('transaction_flow_type_code', transaction.flow_type_id)
        self.add_field(
            'transaction_finance_type_code',
            transaction.finance_type_id
        )

        self.add_field('transaction_aid_type_code', [])
        self.add_field('transaction_aid_type_vocabulary', [])
        for transaction_aid_type in transaction.transactionaidtype_set.all():
            self.add_value_list(
                'transaction_aid_type_code',
                transaction_aid_type.aid_type.code
            )
            self.add_value_list(
                'transaction_aid_type_vocabulary',
                transaction_aid_type.aid_type.vocabulary_id
            )

        self.add_field(
            'transaction_tied_status_code',
            transaction.tied_status_id
        )

        self.add_field(
            'humanitarian',
            bool_string(get_child_attr(transaction, 'activity.humanitarian'))
        )

        self.add_field('sector', [])
        self.add_field('sector_vocabulary', [])
        self.add_field('sector_vocabulary_uri', [])
        self.add_field('sector_code', [])
        self.add_field('sector_percentage', [])
        self.add_field('sector_narrative', [])
        for activity_sector in transaction.activity.activitysector_set.all():
            self.add_value_list(
                'sector',
                JSONRenderer().render(
                    ActivitySectorSerializer(activity_sector).data
                ).decode()
            )

            self.add_value_list(
                'sector_vocabulary',
                activity_sector.vocabulary_id
            )
            self.add_value_list(
                'sector_vocabulary_uri',
                activity_sector.vocabulary_uri
            )
            self.add_value_list('sector_code', activity_sector.sector_id)
            self.add_value_list(
                'sector_percentage',
                decimal_string(activity_sector.percentage)
            )

            for narrative in activity_sector.narratives.all():
                self.add_value_list('sector_narrative', narrative.content)

    def to_representation(self, transaction):
        self.record = transaction

        self.indexing = {}
        self.representation = {}

        self.transaction()
        self.build()

        return self.representation
