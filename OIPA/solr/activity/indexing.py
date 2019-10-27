from rest_framework.renderers import JSONRenderer

from solr.base import BaseIndexing
from solr.utils import bool_string, get_child_attr, value_string, decimal_string
from solr.activity.serializers import RecipientCountrySerializer, ActivityRecipientRegionSerializer, \
    LocationSerializer, ActivitySectorSerializer

from api.activity.serializers import ReportingOrganisationSerializer, TitleSerializer, DescriptionSerializer, \
    ParticipatingOrganisationSerializer, OtherIdentifierSerializer, ActivityDateSerializer, ContactInfoSerializer, \
    CountryBudgetItemsSerializer, HumanitarianScopeSerializer, BudgetSerializer


class ActivityIndexing(BaseIndexing):

    def dataset(self):
        activity = self.record

        self.add_field('dataset_iati_version', activity.iati_standard_version_id)
        self.add_field('dataset_date_created', value_string(get_child_attr(activity, 'dataset.date_created')))
        self.add_field('dataset_date_updated', value_string(get_child_attr(activity, 'dataset.date_updated')))

    def reporting_org(self):
        reporting_org = self.record.reporting_organisations.first()
        if reporting_org:
            self.add_field(
                'reporting_org',
                JSONRenderer().render(ReportingOrganisationSerializer(
                    instance=get_child_attr(reporting_org, 'organisation'),
                    fields=[
                        'ref',
                        'type',
                        'secondary_reporter',
                        'narratives',
                        'activity'
                    ]
                ).data).decode()
            )
            self.add_field('reporting_org_ref', reporting_org.ref)
            self.add_field('reporting_org_type_code', reporting_org.type_id)
            self.add_field('reporting_org_type_name', reporting_org.type.name)
            self.add_field('reporting_org_secondary_reporter',bool_string(reporting_org.secondary_reporter))
            self.add_field('reporting_org_narrative', reporting_org.organisation.primary_name)

    def title(self):
        title = get_child_attr(self.record, 'title')
        if title:
            self.add_field('title', JSONRenderer().render(TitleSerializer(title).data).decode())

            self.add_field('title_narrative', [])
            self.add_field('title_narrative_lang', [])
            self.add_field('title_narrative_text', [])

            self.related_narrative(
                title,
                'title_narrative',
                'title_narrative_text',
                'title_narrative_lang'
            )

    def description(self):
        description_all = self.record.description_set.all()
        if description_all:
            self.add_field('description', [])
            self.add_field('description_type', [])
            self.add_field('description_lang', [])
            self.add_field('description_narrative', [])
            self.add_field('description_narrative_lang', [])
            self.add_field('description_narrative_text', [])

            for description in description_all:
                self.add_value_list(
                    'description',
                    JSONRenderer().render(DescriptionSerializer(description).data).decode()
                )
                self.add_value_list('description_type', description.type_id)

                self.related_narrative(
                    description,
                    'description_narrative',
                    'description_narrative_text',
                    'title_narrative_lang'
                )

    def participating_org(self):
        participating_organisation_all = self.record.participating_organisations.all()
        if participating_organisation_all:
            self.add_field('participating_org', [])
            self.add_field('participating_org_ref', [])
            self.add_field('participating_org_type', [])
            self.add_field('participating_org_role', [])
            self.add_field('participating_org_narrative', [])
            self.add_field('participating_org_narrative_lang', [])
            self.add_field('participating_org_narrative_text', [])

            for participating_organisation in participating_organisation_all:
                self.add_value_list(
                    'participating_org',
                    JSONRenderer().render(
                        ParticipatingOrganisationSerializer(participating_organisation).data
                    ).decode()
                )

                self.add_value_list('participating_org_ref', participating_organisation.ref)
                self.add_value_list('participating_org_type', participating_organisation.type_id)
                self.add_value_list('participating_org_role', participating_organisation.role_id)

                self.related_narrative(
                    participating_organisation,
                    'participating_org_narrative',
                    'participating_org_narrative_text',
                    'participating_org_narrative_lang'
                )

    def other_identifier(self):
        other_identifier_all = self.record.otheridentifier_set.all()
        if other_identifier_all:
            self.add_field('other_identifier', [])
            self.add_field('other_identifier_ref', [])
            self.add_field('other_identifier_type', [])
            self.add_field('other_identifier_owner_org_ref', [])
            self.add_field('other_identifier_owner_org_narrative', [])
            self.add_field('other_identifier_owner_org_narrative_lang', [])
            self.add_field('other_identifier_owner_org_narrative_text', [])

            for other_identifier in other_identifier_all:
                self.add_value_list(
                    'other_identifier',
                    JSONRenderer().render(
                        OtherIdentifierSerializer(other_identifier).data
                    ).decode()
                )

                self.add_value_list('other_identifier_ref', other_identifier.identifier)
                self.add_value_list('other_identifier_type', other_identifier.type_id)
                self.add_value_list('other_identifier_owner_org_ref', other_identifier.owner_ref)

                self.related_narrative(
                    other_identifier,
                    'other_identifier_owner_org_narrative',
                    'other_identifier_owner_org_narrative_text',
                    'other_identifier_owner_org_narrative_lang'
                )

    def activity_date(self):
        activity_dates_all = self.record.activitydate_set.all()
        if activity_dates_all:
            self.add_field('activity_date', [])
            self.add_field('activity_date_type', [])
            self.add_field('activity_dates_iso_date', [])

            self.add_field('activity_date_narrative', [])
            self.add_field('activity_date_narrative_lang', [])
            self.add_field('activity_date_narrative_text', [])

            for activity_date in activity_dates_all:
                self.add_value_list(
                    'activity_date',
                    JSONRenderer().render(
                        ActivityDateSerializer(activity_date).data
                    ).decode()
                )

                self.add_value_list('activity_date_type', activity_date.type_id)

                if activity_date.iso_date:
                    self.add_value_list('activity_dates_iso_date', value_string(activity_date.iso_date))

                if activity_date.type_id == '1':
                    self.add_field('activity_date_start_planned', value_string(activity_date.iso_date))
                elif activity_date.type_id == '2':
                    self.add_field('activity_date_start_actual', value_string(activity_date.iso_date))
                elif activity_date.type_id == '3':
                    self.add_field('activity_date_end_planned', value_string(activity_date.iso_date))
                elif activity_date.type_id == '4':
                    self.add_field('activity_date_end_actual', value_string(activity_date.iso_date))

                self.related_narrative(
                    activity_date,
                    'activity_date_narrative',
                    'activity_date_narrative_text',
                    'activity_date_narrative_lang'
                )

    def contact_info(self):
        contact_info_all = self.record.contactinfo_set.all()
        if contact_info_all:
            self.add_field('contact_info', [])

            self.add_field('contact_info_type', [])
            self.add_field('contact_info_telephone', [])
            self.add_field('contact_info_email', [])
            self.add_field('contact_info_website', [])

            self.add_field('contact_info_organisation_narrative', [])
            self.add_field('contact_info_organisation_narrative_lang', [])
            self.add_field('contact_info_organisation_narrative_text', [])

            self.add_field('contact_info_department_narrative', [])
            self.add_field('contact_info_department_narrative_lang', [])
            self.add_field('contact_info_department_narrative_text', [])

            self.add_field('contact_info_person_name_narrative', [])
            self.add_field('contact_info_person_name_narrative_lang', [])
            self.add_field('contact_info_person_name_narrative_text', [])

            self.add_field('contact_info_job_title_narrative', [])
            self.add_field('contact_info_job_title_narrative_lang', [])
            self.add_field('contact_info_job_title_narrative_text', [])

            self.add_field('contact_info_mailing_address_narrative', [])
            self.add_field('contact_info_mailing_address_narrative_lang', [])
            self.add_field('contact_info_mailing_address_narrative_text', [])

            for contact_info in contact_info_all:
                self.add_value_list(
                    'contact_info',
                    JSONRenderer().render(
                        ContactInfoSerializer(contact_info).data
                    ).decode()
                )

                self.add_value_list('contact_info_type', contact_info.type_id)
                self.add_value_list('contact_info_telephone', contact_info.telephone)
                self.add_value_list('contact_info_email', contact_info.email)
                self.add_value_list('contact_info_website', contact_info.website)

                self.related_narrative(
                    get_child_attr(contact_info, 'organisation'),
                    'contact_info_organisation_narrative',
                    'contact_info_organisation_narrative_text',
                    'contact_info_organisation_narrative_lang'
                )
                self.related_narrative(
                    get_child_attr(contact_info, 'department'),
                    'contact_info_department_narrative',
                    'contact_info_department_narrative_text',
                    'contact_info_department_narrative_lang'
                )
                self.related_narrative(
                    get_child_attr(contact_info, 'person_name'),
                    'contact_info_person_name_narrative',
                    'contact_info_person_name_narrative_text',
                    'contact_info_person_name_narrative_lang'
                )
                self.related_narrative(
                    get_child_attr(contact_info, 'job_title'),
                    'contact_info_job_title_narrative',
                    'contact_info_job_title_narrative_text',
                    'contact_info_job_title_narrative_lang'
                )
                self.related_narrative(
                    get_child_attr(contact_info, 'mailing_address'),
                    'contact_info_mailing_address_narrative',
                    'contact_info_mailing_address_narrative_text',
                    'contact_info_mailing_address_narrative_lang'
                )

    def recipient_country(self):
        recipient_country_all = self.record.activityrecipientcountry_set.all()
        if recipient_country_all:
            self.add_field('recipient_country', [])

            self.add_field('recipient_country_code', [])
            self.add_field('recipient_country_name', [])
            self.add_field('recipient_country_percentage', [])

            self.add_field('recipient_country_narrative', [])
            self.add_field('recipient_country_narrative_lang', [])
            self.add_field('recipient_country_narrative_text', [])

            for recipient_country in recipient_country_all:
                self.add_value_list(
                    'recipient_country',
                    JSONRenderer().render(
                        RecipientCountrySerializer(recipient_country).data
                    ).decode()
                )

                self.add_value_list('recipient_country_code', recipient_country.country.code)
                self.add_value_list('recipient_country_name', recipient_country.country.name)
                self.add_value_list('recipient_country_percentage', decimal_string(recipient_country.percentage))

                self.related_narrative(
                    recipient_country,
                    'recipient_country_narrative',
                    'recipient_country_narrative_text',
                    'recipient_country_narrative_lang'
                )

    def recipient_region(self):
        recipient_region_all = self.record.activityrecipientregion_set.all()
        if recipient_region_all:
            self.add_field('recipient_region', [])

            self.add_field('recipient_region_code', [])
            self.add_field('recipient_region_name', [])
            self.add_field('recipient_region_vocabulary', [])
            self.add_field('recipient_region_vocabulary_uri', [])
            self.add_field('recipient_region_percentage', [])

            self.add_field('recipient_region_narrative', [])
            self.add_field('recipient_region_narrative_lang', [])
            self.add_field('recipient_region_narrative_text', [])

            for recipient_region in recipient_region_all:
                self.add_value_list(
                    'recipient_region',
                    JSONRenderer().render(
                        ActivityRecipientRegionSerializer(recipient_region).data
                    ).decode()
                )

                self.add_value_list('recipient_region_code', recipient_region.region.code)
                self.add_value_list('recipient_region_name', recipient_region.region.name)
                self.add_value_list('recipient_region_vocabulary', recipient_region.vocabulary.code)
                self.add_value_list('recipient_region_vocabulary_uri', recipient_region.vocabulary_uri)
                self.add_value_list('recipient_region_percentage', decimal_string(recipient_region.percentage))

                self.related_narrative(
                    recipient_region,
                    'recipient_region_narrative',
                    'recipient_region_narrative_text',
                    'recipient_region_narrative_lang'
                )

    def location(self):
        locations_all = self.record.location_set.all()
        if locations_all:
            self.add_field('location', [])

            self.add_field('location_ref', [])
            self.add_field('location_reach_code', [])
            self.add_field('location_id_vocabulary', [])
            self.add_field('location_id_code', [])
            self.add_field('location_point_pos', [])
            self.add_field('location_exactness_code', [])
            self.add_field('location_class_code', [])
            self.add_field('location_feature_designation_code', [])

            self.add_field('location_name_narrative', [])
            self.add_field('location_name_narrative_lang', [])
            self.add_field('location_name_narrative_text', [])

            self.add_field('location_description_narrative', [])
            self.add_field('location_description_narrative_lang', [])
            self.add_field('location_description_narrative_text', [])

            self.add_field('location_activity_description_narrative', [])
            self.add_field('location_activity_description_narrative_lang', [])
            self.add_field('location_activity_description_narrative_text', [])

            self.add_field('location_administrative_vocabulary', [])
            self.add_field('location_administrative_level', [])
            self.add_field('location_administrative_code', [])

            for location in locations_all:
                self.add_value_list(
                    'location',
                    JSONRenderer().render(
                        LocationSerializer(location).data
                    ).decode()
                )

                self.add_value_list('location_ref', location.ref)
                self.add_value_list('location_reach_code', location.location_reach_id)
                self.add_value_list('location_id_vocabulary', location.location_id_vocabulary_id)
                self.add_value_list('location_id_code', location.location_id_code)
                self.add_value_list('location_point_pos', value_string(location.point_pos.coords))
                self.add_value_list('location_exactness_code', location.exactness_id)
                self.add_value_list('location_class_code', location.location_class_id)
                self.add_value_list('location_feature_designation_code', location.feature_designation_id)

                self.related_narrative(
                    get_child_attr(location, 'name'),
                    'location_name_narrative',
                    'location_name_narrative_text',
                    'location_name_narrative_lang'
                )
                self.related_narrative(
                    get_child_attr(location, 'description'),
                    'location_description_narrative',
                    'location_description_narrative_text',
                    'location_description_narrative_lang'
                )
                self.related_narrative(
                    get_child_attr(location, 'activity_description'),
                    'location_activity_description_narrative',
                    'location_activity_description_narrative_text',
                    'location_activity_description_narrative_lang'
                )

                for location_administrative in location.locationadministrative_set.all():
                    self.add_value_list('location_administrative_vocabulary', location_administrative.vocabulary.code)
                    self.add_value_list('location_administrative_level', location_administrative.level)
                    self.add_value_list('location_administrative_code', location_administrative.code)

    def sector(self):
        activity_sector_all = self.record.activitysector_set.all()
        if activity_sector_all:
            self.add_field('sector', [])

            self.add_field('sector_vocabulary', [])
            self.add_field('sector_vocabulary_uri', [])
            self.add_field('sector_code', [])
            self.add_field('sector_percentage', [])

            self.add_field('sector_narrative', [])
            self.add_field('sector_narrative_lang', [])
            self.add_field('sector_narrative_text', [])

            for activity_sector in activity_sector_all:
                self.add_value_list(
                    'sector',
                    JSONRenderer().render(
                        ActivitySectorSerializer(activity_sector).data
                    ).decode()
                )

                self.add_value_list('sector_vocabulary', activity_sector.vocabulary_id)
                self.add_value_list('sector_vocabulary_uri', activity_sector.vocabulary_uri)
                self.add_value_list('sector_code', activity_sector.sector.code)
                self.add_value_list('sector_percentage', decimal_string(activity_sector.percentage))

                self.related_narrative(
                    activity_sector,
                    'sector_narrative',
                    'sector_narrative_text',
                    'sector_narrative_lang'
                )

    def country_budget_items(self):
        country_budget_item = get_child_attr(self.record, 'country_budget_items')
        if country_budget_item:
            self.add_field(
                'country_budget_items',
                JSONRenderer().render(
                    CountryBudgetItemsSerializer(country_budget_item).data
                ).decode()
            )

            self.add_field('country_budget_items_vocabulary', country_budget_item.vocabulary_id)

            self.add_field('country_budget_items_budget_item_code', [])
            self.add_field('country_budget_items_budget_item_percentage', [])

            self.add_field('country_budget_items_budget_description_narrative', [])
            self.add_field('country_budget_items_budget_description_narrative_lang', [])
            self.add_field('country_budget_items_budget_description_narrative_text', [])

            for budget_item in country_budget_item.budgetitem_set.all():
                self.add_value_list('country_budget_items_budget_item_code', budget_item.code_id)
                self.add_value_list(
                    'country_budget_items_budget_item_percentage',
                    decimal_string(budget_item.percentage)
                )

                self.related_narrative(
                    get_child_attr(budget_item, 'description'),
                    'country_budget_items_budget_description_narrative',
                    'country_budget_items_budget_description_narrative_text',
                    'country_budget_items_budget_description_narrative_lang'
                )

    def humanitarian_scope(self):
        humanitarian_scope_all = self.record.humanitarianscope_set.all()
        if humanitarian_scope_all:
            self.add_field('humanitarian_scope', [])

            self.add_field('humanitarian_scope_type', [])
            self.add_field('humanitarian_scope_vocabulary', [])
            self.add_field('humanitarian_scope_vocabulary_uri', [])
            self.add_field('humanitarian_scope_code', [])

            self.add_field('humanitarian_scope_narrative', [])
            self.add_field('humanitarian_scope_narrative_lang', [])
            self.add_field('humanitarian_scope_narrative_text', [])

            for humanitarian_scope in humanitarian_scope_all:
                self.add_value_list(
                    'humanitarian_scope',
                    JSONRenderer().render(
                        HumanitarianScopeSerializer(humanitarian_scope).data
                    ).decode()
                )

                self.add_value_list('humanitarian_scope_type', humanitarian_scope.type_id)
                self.add_value_list('humanitarian_scope_vocabulary', humanitarian_scope.vocabulary_id)
                self.add_value_list('humanitarian_scope_vocabulary_uri', humanitarian_scope.vocabulary_uri)
                self.add_value_list('humanitarian_scope_code', humanitarian_scope.code)

                self.related_narrative(
                    humanitarian_scope,
                    'humanitarian_scope_narrative',
                    'humanitarian_scope_narrative_text',
                    'humanitarian_scope_narrative_lang'
                )

    def budget(self):
        budget_all = self.record.budget_set.all()
        if budget_all:
            self.add_field('budget', [])
            self.add_field('budget_type', [])
            self.add_field('budget_status', [])
            self.add_field('budget_period_start_iso_date', [])
            self.add_field('budget_period_end_iso_date', [])
            self.add_field('budget_value_currency', [])
            self.add_field('budget_value_date', [])
            self.add_field('budget_value', [])

            for budget in budget_all:
                self.add_value_list(
                    'budget',
                    JSONRenderer().render(
                        BudgetSerializer(budget).data
                    ).decode()
                )

                self.add_value_list('budget_type', budget.type_id)
                self.add_value_list('budget_status', budget.status_id)
                self.add_value_list('budget_period_start_iso_date', value_string(budget.period_start))
                self.add_value_list('budget_period_end_iso_date', value_string(budget.period_end))
                self.add_value_list('budget_value_currency', budget.currency_id)
                self.add_value_list('budget_value_date', value_string(budget.value_date) )
                self.add_value_list('budget_value', decimal_string(budget.value))

    def activity(self):
        activity = self.record

        self.add_field('id', value_string(activity.id))
        self.add_field('iati_identifier', activity.iati_identifier)
        self.add_field('default_lang', activity.default_lang_id)
        self.add_field('default_currency', activity.default_currency_id)
        self.add_field('humanitarian', bool_string(activity.humanitarian))
        self.add_field('hierarchy', value_string(activity.hierarchy))
        self.add_field('linked_data_uri', activity.linked_data_uri)
        self.add_field('activity_status_code', activity.activity_status_id)
        self.add_field('activity_scope_code', activity.scope_id)
        self.add_field('collaboration_type_code', activity.collaboration_type_id)
        self.add_field('default_flow_type_code', activity.default_flow_type_id)
        self.add_field('default_finance_type_code', activity.default_finance_type_id)
        self.add_field('default_tied_status_code', activity.default_tied_status_id)
        self.add_field('capital_spend_percentage', decimal_string(activity.capital_spend))

        self.dataset()
        self.reporting_org()
        self.title()
        self.description()
        self.participating_org()
        self.other_identifier()
        self.activity_date()
        self.contact_info()
        self.recipient_country()
        self.recipient_region()
        self.location()
        self.sector()
        self.country_budget_items()
        self.humanitarian_scope()
        self.budget()

    def to_representation(self, activity):
        self.record = activity

        self.indexing = {}
        self.representation = {}

        self.activity()
        self.build()

        return self.representation
