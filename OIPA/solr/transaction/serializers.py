from solr.base import IndexingSerializer
from solr.utils import bool_string, value_string, decimal_string, get_narrative_lang_list


class TransactionSerializer(IndexingSerializer):

    def transaction(self, transaction):
        self.add_field('iati_identifier')
        self.add_field('title_lang')
        self.add_field('title_narrative')

        self.add_field('description_type')
        self.add_field('description_lang')
        self.add_field('description_narrative')

        self.add_field('activity_date_type')
        self.add_field('activity_date_iso_date')

        self.add_field('reporting_org_ref')
        self.add_field('reporting_org_type')
        self.add_field('reporting_org_secondary_reporter')
        self.add_field('reporting_org_narrative')

        self.add_field('transaction_ref')
        self.add_field('transaction_humanitarian')
        self.add_field('transaction_type')
        self.add_field('transaction_date_iso_date')
        self.add_field('transaction_value_currency')
        self.add_field('transaction_value_date')
        self.add_field('transaction_value')

        self.add_field('transaction_provider_org_provider_activity_id')
        self.add_field('transaction_provider_org_type')
        self.add_field('transaction_provider_org_ref')

        self.add_field('transaction_provider_org_narrative')
        self.add_field('transaction_provider_org_narrative_lang')
        self.add_field('transaction_provider_org_narrative_text')

        self.add_field('transaction_receiver_org_receiver_activity_id')
        self.add_field('transaction_receiver_org_type')
        self.add_field('transaction_receiver_org_ref')

        self.add_field('transaction_receiver_org_narrative')
        self.add_field('transaction_receiver_org_narrative_lang')
        self.add_field('transaction_receiver_org_narrative_text')

        self.add_field('transaction_disburstment_channel_code')

        self.add_field('transaction_sector_vocabulary')
        self.add_field('transaction_sector_vocabulary_uri')
        self.add_field('transaction_sector_code')

        self.add_field('transaction_recipient_country_code')
        self.add_field('transaction_recipient_region_code')
        self.add_field('transaction_recipient_region_vocabulary')
        self.add_field('transaction_flow_type_code')
        self.add_field('transaction_finance_type_code')

        self.add_field('transaction_aid_type_code')
        self.add_field('transaction_aid_type_vocabulary')
        self.add_field('transaction_tied_status_code')

        self.indexing['iati_identifier'] = getattr(transaction.activity, 'iati_identifier', None)
        self.indexing['title_lang'], self.indexing['title_narrative'] = \
            get_narrative_lang_list(transaction.activity.title)

        for description in transaction.activity.description_set.all():
            self.add_value(
                'description_type',
                description.type_id
            )
            for narrative in description.narratives.all():
                self.add_value(
                    'description_narrative',
                    narrative.content
                )
                self.add_value(
                    'description_lang',
                    narrative.language_id
                )

        for reporting_organisation in transaction.activity.reporting_organisations.all():
            self.add_value(
                'reporting_org_ref',
                reporting_organisation.ref
            )
            self.add_value(
                'reporting_org_type',
                reporting_organisation.type_id
            )
            self.add_value(
                'reporting_org_secondary_reporter',
                bool_string(reporting_organisation.secondary_reporter)
            )
            self.add_value(
                'reporting_org_narrative',
                getattr(reporting_organisation.organisation, 'primary_name', None)
            )

        self.add_value(
            'transaction_ref',
            transaction.ref
        )
        self.add_value(
            'transaction_humanitarian',
            bool_string(transaction.humanitarian)
        )
        self.add_value(
            'transaction_type',
            transaction.transaction_type_id
        )
        self.add_value(
            'transaction_date_iso_date',
            value_string(transaction.transaction_date)
        )
        self.add_value(
            'transaction_value_currency',
            transaction.currency_id
        )
        self.add_value(
            'transaction_value_date',
            value_string(transaction.value_date)
        )
        self.add_value(
            'transaction_value',
            decimal_string(transaction.value)
        )
        self.add_value(
            'transaction_provider_org_provider_activity_id',
            getattr(transaction, 'provider_organisation.provider_activity_ref', None)
        )
        self.add_value(
            'transaction_provider_org_type',
            getattr(transaction, 'provider_organisation.type_id', None)
        )
        self.add_value(
            'transaction_provider_org_ref',
            getattr(transaction, 'provider_organisation.ref', None)
        )

        provider_organisation = getattr(transaction, 'provider_organisation', None)
        if provider_organisation:
            for narrative in provider_organisation.narratives.all():
                self.add_value(
                    'transaction_provider_org_narrative',
                    narrative.content
                )
                self.add_value(
                    'transaction_provider_org_narrative_text',
                    narrative.content
                )
                self.add_value(
                    'transaction_provider_org_narrative_lang',
                    narrative.language_id
                )

        self.add_value(
            'transaction_receiver_org_receiver_activity_id',
            getattr(transaction, 'receiver_organisation.receiver_activity_ref', None)
        )
        self.add_value(
            'transaction_receiver_org_type',
            getattr(transaction, 'receiver_organisation.type_id', None)
        )
        self.add_value(
            'transaction_receiver_org_ref',
            getattr(transaction, 'receiver_organisation.ref', None)
        )
        receiver_organisation = getattr(transaction, 'receiver_organisation', None)
        if receiver_organisation:
            for narrative in receiver_organisation.narratives.all():
                self.add_value(
                    'transaction_receiver_org_narrative',
                    narrative.content
                )
                self.add_value(
                    'transaction_receiver_org_narrative_text',
                    narrative.content
                )
                self.add_value(
                    'transaction_receiver_org_narrative_lang',
                    narrative.language_id
                )

        self.add_value(
            'transaction_disburstment_channel_code',
            transaction.disbursement_channel_id
        )

        for transaction_sector in transaction.transactionsector_set.all():
            self.add_value(
                'transaction_sector_vocabulary',
                transaction_sector.vocabulary_id
            )
            self.add_value(
                'transaction_sector_vocabulary_uri',
                transaction_sector.vocabulary_uri
            )
            self.add_value(
                'transaction_sector_code',
                transaction_sector.sector_id
            )

        for transaction_recipient_country in transaction.transactionrecipientcountry_set.all():
            self.add_value(
                'transaction_recipient_country_code',
                transaction_recipient_country.country_id
            )

        for transaction_recipient_region in transaction.transactionrecipientregion_set.all():
            self.add_value(
                'transaction_recipient_region_code',
                transaction_recipient_region.region_id
            )
            self.add_value(
                'transaction_recipient_region_vocabulary',
                transaction_recipient_region.vocabulary_id
            )

        self.add_value(
            'transaction_flow_type_code',
            transaction.flow_type_id
        )
        self.add_value(
            'transaction_finance_type_code',
            transaction.finance_type_id
        )

        for transaction_aid_type in transaction.transactionaidtype_set.all():
            self.add_value(
                'transaction_aid_type_code',
                transaction_aid_type.aid_type.code
            )
            self.add_value(
                'transaction_aid_type_vocabulary',
                transaction_aid_type.aid_type.vocabulary_id
            )

        self.add_value(
            'transaction_tied_status_code',
            transaction.tied_status_id
        )

    def to_representation(self, transaction):
        self.transaction(transaction)
        self.build()

        return self.representation
