from solr.indexing import BaseIndexing
from solr.utils import add_reporting_org, bool_string, date_string, decimal_string, get_child_attr, value_string


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


def add_sector(serializer, activity):
    sector_all = activity.activitysector_set.all()
    if sector_all:
        serializer.add_field('sector_code', [])
        serializer.add_field('sector_vocabulary', [])
        for sector in sector_all:
            serializer.add_value_list('sector_code', sector.sector.code)
            serializer.add_value_list('sector_vocabulary',
                                      sector.sector.vocabulary_id)


def add_recipient_region(serializer, activity):
    recipient_region_all = activity.activityrecipientregion_set.all()
    if recipient_region_all:
        serializer.add_field('recipient_region_code', [])

        for recipient_region in recipient_region_all:
            serializer.add_value_list('recipient_region_code',
                                      recipient_region.region.code)


def add_activity_date(serializer, activity):
    activity_date_all = activity.activitydate_set.all()
    common_start = None
    common_end = None
    if activity_date_all:
        for activity_date in activity_date_all:
            if activity_date.type_id == '1':
                serializer.add_field(
                    'activity_date_start_planned_f',
                    activity_date.iso_date
                )
                if not common_start:
                    common_start = activity_date.iso_date
            elif activity_date.type_id == '2':
                serializer.add_field(
                    'activity_date_start_actual_f',
                    activity_date.iso_date
                )
                common_start = activity_date.iso_date
            elif activity_date.type_id == '3':
                serializer.add_field(
                    'activity_date_end_planned_f',
                    activity_date.iso_date
                )
                if not common_end:
                    common_end = activity_date.iso_date
            elif activity_date.type_id == '4':
                serializer.add_field(
                    'activity_date_end_actual_f',
                    activity_date.iso_date
                )
                common_end = activity_date.iso_date
    if common_start:
        serializer.add_field('activity_date_start_common_f', common_start)
    if common_end:
        serializer.add_field('activity_date_end_common_f', common_end)


def add_participating_org(serializer, activity):
    participating_org_all = activity.participating_organisations.all()
    if participating_org_all:
        serializer.add_field('participating_org_ref', [])
        serializer.add_field('participating_org_type', [])
        serializer.add_field('participating_org_narrative', [])
        serializer.add_field('participating_org_narrative_lang', [])
        serializer.add_field('participating_org_narrative_text', [])
        for participating_organisation in participating_org_all:
            serializer.add_value_list(
                'participating_org_ref',
                participating_organisation.ref
            )
            serializer.add_value_list(
                'participating_org_type',
                participating_organisation.type_id
            )
            for narrative in participating_organisation.narratives.all():
                if narrative.content:
                    serializer.add_value_list(
                        "participating_org_narrative",
                        narrative.content
                    )
                    serializer.add_value_list(
                        "participating_org_narrative_text",
                        narrative.content
                    )
                else:
                    serializer.add_value_list(
                        "participating_org_narrative",
                        " "
                    )
                    serializer.add_value_list(
                        "participating_org_narrative_text",
                        " "
                    )

                if narrative.language:
                    serializer.add_value_list(
                        "participating_org_narrative_lang",
                        narrative.language.code
                    )
                else:
                    serializer.add_value_list(
                        "participating_org_narrative_lang",
                        " "
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
    serializer.add_field('default_humanitarian', bool_string(
        activity.humanitarian))
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
        serializer.add_field('tag_vocabulary', [])

        for tag in tag_all:
            serializer.add_value_list(
                'tag_code',
                tag.code
            )
            serializer.add_value_list(
                'tag_vocabulary',
                tag.vocabulary_id
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
            'budget_value_usd',
            decimal_string(budget.usd_value)
        )
        self.add_field(
            'budget_imf_link',
            budget.imf_url
        )
        self.add_field(
            'budget_usd_conversion_rate',
            decimal_string(budget.usd_exchange_rate)
        )

        add_reporting_org(self, budget.activity)
        add_recipient_country(self, budget.activity)
        add_recipient_region(self, budget.activity)
        add_sector(self, budget.activity)
        add_activity_date(self, budget.activity)
        add_participating_org(self, budget.activity)
        add_activity_additional_filter_fields(self, budget.activity)

    def to_representation(self, budget):
        self.record = budget
        self.indexing = {}
        self.representation = {}

        self.budget()
        self.build()

        return self.representation
