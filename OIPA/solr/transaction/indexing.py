from solr.indexing import BaseIndexing
from solr.utils import (
    add_reporting_org, bool_string, date_string, decimal_string,
    get_child_attr, get_narrative_lang_list, value_string
)


def add_participating_org(serializer, activity):
    participating_org_all = activity.participating_organisations.all()
    if participating_org_all:
        serializer.add_field('participating_org_ref', [])
        for participating_organisation in participating_org_all:
            serializer.add_value_list(
                'participating_org_ref',
                participating_organisation.ref
            )
            

def add_activity_additional_filter_fields(serializer, activity):
    serializer.add_field('activity_scope_code', activity.scope_id)
    serializer.add_field('activity_status_code', activity.activity_status_id)
    serializer.add_field('collaboration_type_code',
                         activity.collaboration_type_id
                         )
    serializer.add_field('default_currency', activity.default_currency_id)
    serializer.add_field(
        'default_finance_type_code',
        activity.default_finance_type_id
    )
    serializer.add_field('default_lang', activity.default_lang_id)
    serializer.add_field('default_flow_type_code',
                         activity.default_flow_type_id)
    serializer.add_field(
        'default_tied_status_code',
        activity.default_tied_status_id
    )
    serializer.add_field('hierarchy', value_string(activity.hierarchy))
    serializer.add_field('humanitarian', bool_string(activity.humanitarian))
    serializer.add_field(
        'dataset_iati_version',
        activity.iati_standard_version_id)

    # default-aid-type
    default_aid_type_all = activity.default_aid_types.all()
    if default_aid_type_all:
        serializer.add_field('default_aid_type_code', [])
        serializer.add_field('default_aid_type_vocabulary', [])
        serializer.add_field('default_aid_type_category_code', [])

        for default_aid_type in default_aid_type_all:
            serializer.add_value_list(
                'default_aid_type_code',
                get_child_attr(
                    default_aid_type,
                    'aid_type.code'
                )
            )
            serializer.add_value_list(
                'default_aid_type_vocabulary',
                get_child_attr(
                    default_aid_type,
                    'aid_type.vocabulary.code'
                )
            )
            serializer.add_value_list(
                'default_aid_type_category_code',
                get_child_attr(
                    default_aid_type,
                    'aid_type.category.code'
                )
            )

    # document-link-category-code
    # we want to get only activity/document-link not other document-links
    document_link_all = activity.documentlink_set.filter(
            result_id__isnull=True,
            result_indicator_id__isnull=True,
            result_indicator_baseline_id__isnull=True,
            result_indicator_period_actual_id__isnull=True,
            result_indicator_period_target_id__isnull=True
        )
    if document_link_all:
        serializer.add_field('document_link_category_code', [])

        for document_link in document_link_all:
            for document_link_category in \
                    document_link.documentlinkcategory_set.all():
                serializer.add_value_list(
                    'document_link_category_code',
                    document_link_category.category_id
                )

    # humanitarian scope
    humanitarian_scope_all = activity.humanitarianscope_set.all()
    if humanitarian_scope_all:
        serializer.add_field('humanitarian_scope_type', [])
        serializer.add_field('humanitarian_scope_vocabulary', [])

        for humanitarian_scope in humanitarian_scope_all:
            serializer.add_value_list(
                'humanitarian_scope_type',
                humanitarian_scope.type_id
            )
            serializer.add_value_list(
                'humanitarian_scope_vocabulary',
                humanitarian_scope.vocabulary_id
            )

    # other-identifier
    other_identifier_all = activity.otheridentifier_set.all()
    if other_identifier_all:
        serializer.add_field('other_identifier_type', [])

        for other_identifier in other_identifier_all:
            serializer.add_value_list(
                'other_identifier_type',
                other_identifier.type_id
            )

    # policy-marker
    policy_marker_all = activity.activitypolicymarker_set.all()
    if policy_marker_all:
        serializer.add_field('policy_marker_code', [])

        for policy_marker in policy_marker_all:
            serializer.add_value_list(
                'policy_marker_code',
                policy_marker.code_id
            )

    # tag
    tag_all = activity.activitytag_set.all()
    if tag_all:
        serializer.add_field('tag_code', [])

        for tag in tag_all:
            serializer.add_value_list(
                'tag_code',
                tag.code
            )


class TransactionIndexing(BaseIndexing):

    def transaction(self):
        transaction = self.record

        self.add_field('id', transaction.id)
        self.add_field('iati_identifier', transaction.activity.iati_identifier)
        if get_child_attr(transaction, 'activity.title'):
            self.indexing['title_lang'], self.indexing['title_narrative'] = \
                get_narrative_lang_list(transaction.activity.title)

        self.add_field('activity_description_type', [])
        self.add_field('activity_description_narrative', [])
        for description in transaction.activity.description_set.all():
            self.add_value_list(
                'activity_description_type',
                description.type_id
            )
            for narrative in description.narratives.all():
                self.add_value_list(
                    'activity_description_narrative',
                    narrative.content
                )

        self.add_field('activity_date_type', [])
        self.add_field('activity_date_iso_date', [])

        add_reporting_org(self, transaction.activity)
        recipient_country_all = transaction.activity.\
            activityrecipientcountry_set.all()
        if recipient_country_all:
            self.add_field('activity_recipient_country_code', [])
            self.add_field('activity_recipient_country_name', [])
            for recipient_country in recipient_country_all:

                self.add_value_list(
                    'activity_recipient_country_code',
                    recipient_country.country.code
                )
                self.add_value_list(
                    'activity_recipient_country_name',
                    recipient_country.country.name
                )

        recipient_region_all = transaction.activity.\
            activityrecipientregion_set.all()
        if recipient_region_all:
            self.add_field('activity_recipient_region_code', [])
            self.add_field('activity_recipient_region_name', [])

            for recipient_region in recipient_region_all:

                self.add_value_list(
                    'activity_recipient_region_code',
                    recipient_region.region.code
                )
                self.add_value_list(
                    'activity_recipient_region_name',
                    recipient_region.region.name
                )

        if get_child_attr(transaction, 'description'):
            self.indexing['transaction_description_lang'], self.indexing[
                'transaction_description_narrative'] = \
                get_narrative_lang_list(transaction.description)

        self.add_field('transaction_ref', transaction.ref)
        self.add_field(
            'transaction_humanitarian',
            bool_string(transaction.humanitarian)
        )
        self.add_field('transaction_type', transaction.transaction_type_id)
        self.add_field(
            'transaction_date_iso_date',
            str(transaction.transaction_date)
        )
        self.add_field(
            'transaction_date_iso_date_f',
            date_string(transaction.transaction_date)
        )
        self.add_field('transaction_value_currency', transaction.currency_id)
        self.add_field(
            'transaction_value_date',
            date_string(transaction.value_date)
        )
        self.add_field('transaction_value', decimal_string(transaction.value))

        self.add_field(
            'transaction_value_usd',
            decimal_string(transaction.usd_value)
        )
        self.add_field(
            'transaction_imf_link',
            transaction.imf_url
        )
        self.add_field(
            'transaction_usd_conversion_rate',
            decimal_string(transaction.usd_exchange_rate)
        )

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
            'transaction_disbursement_channel_code',
            transaction.disbursement_channel_id
        )

        self.add_field('transaction_sector_vocabulary', [])
        self.add_field('transaction_sector_vocabulary_uri', [])
        self.add_field('transaction_sector_code', [])
        for sector in transaction.transactionsector_set.all():
            self.add_value_list(
                'transaction_sector_vocabulary',
                sector.vocabulary_id
            )
            self.add_value_list(
                'transaction_sector_vocabulary_uri',
                sector.vocabulary_uri
            )
            self.add_value_list(
                'transaction_sector_code',
                sector.sector.code
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

        self.add_field('activity_sector_vocabulary', [])
        self.add_field('activity_sector_code', [])

        for activity_sector in transaction.activity.activitysector_set.all():

            self.add_value_list(
                'activity_sector_vocabulary',
                activity_sector.vocabulary_id
            )
            self.add_value_list('activity_sector_code',
                                activity_sector.sector.code)
            
        add_participating_org(self, transaction.activity)
        add_activity_additional_filter_fields(self, transaction.activity)

    def to_representation(self, transaction):
        self.record = transaction

        self.indexing = {}
        self.representation = {}

        self.transaction()
        self.build()

        return self.representation
