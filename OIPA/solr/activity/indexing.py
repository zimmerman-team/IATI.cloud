from rest_framework.renderers import JSONRenderer

from api.activity.serializers import (
    ActivityDateSerializer, ActivityDefaultAidTypeSerializer,
    ActivityPolicyMarkerSerializer, ActivityTagSerializer, BudgetSerializer,
    ConditionsSerializer, ContactInfoSerializer, CountryBudgetItemsSerializer,
    CrsAddSerializer, DescriptionSerializer, DocumentLinkSerializer,
    FssSerializer, HumanitarianScopeSerializer, LegacyDataSerializer,
    OtherIdentifierSerializer, ParticipatingOrganisationSerializer,
    PlannedDisbursementSerializer, RelatedActivitySerializer,
    ReportingOrganisationSerializer, TitleSerializer
)
from solr.activity.references import (
    ActivityDateReference, ActivityScopeReference, ActivityStatusReference,
    CapitalSpendReference, CollaborationTypeReference, ConditionsReference,
    ContactInfoReference, CountryBudgetItemsReference, CrsAddReference,
    DefaultAidTypeReference, DefaultFinanceTypeReference,
    DefaultFlowTypeReference, DefaultTiedStatusReference, DescriptionReference,
    DocumentLinkReference, FssReference, HumanitarianScopeReference,
    LegacyDataReference, LocationReference, OtherIdentifierReference,
    ParticipatingOrgReference, PlannedDisbursementReference,
    PolicyMarkerReference, RecipientCountryReference, RecipientRegionReference,
    RelatedActivityReference, ReportingOrgReference, SectorReference,
    TagReference, TitleReference
)
from solr.activity.serializers import (
    ActivityRecipientRegionSerializer, ActivitySectorSerializer,
    LocationSerializer, RecipientCountrySerializer
)
from solr.budget.references import BudgetReference
from solr.indexing import BaseIndexing
from solr.result.references import ResultReference
from solr.result.serializers import ResultSerializer
from solr.transaction.references import TransactionReference
from solr.transaction.serializers import TransactionSerializer
from solr.utils import (
    bool_string, date_string, decimal_string, get_child_attr, value_string
)


class ActivityIndexing(BaseIndexing):

    def dataset(self):
        activity = self.record

        self.add_field(
            'dataset_iati_version',
            activity.iati_standard_version_id)
        self.add_field(
            'dataset_date_created',
            date_string(get_child_attr(activity, 'dataset.date_created'))
        )
        self.add_field(
            'dataset_date_updated',
            date_string(get_child_attr(activity, 'dataset.date_updated'))
        )

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
            self.add_field(
                'reporting_org_xml',
                ReportingOrgReference(
                    reporting_org=get_child_attr(reporting_org, 'organisation')
                ).to_string()
            )

            self.add_field('reporting_org_ref', reporting_org.ref)
            self.add_field('reporting_org_type_code', reporting_org.type_id)
            self.add_field(
                'reporting_org_type_name',
                get_child_attr(reporting_org, 'type.name')
            )
            self.add_field(
                'reporting_org_secondary_reporter',
                bool_string(reporting_org.secondary_reporter)
            )
            self.add_field(
                'reporting_org_narrative',
                reporting_org.organisation.primary_name
            )

    def title(self):
        title = get_child_attr(self.record, 'title')
        if title:
            self.add_field(
                'title',
                JSONRenderer().render(TitleSerializer(title).data).decode()
            )
            self.add_field(
                'title_xml',
                TitleReference(title=title).to_string()
            )

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
            self.add_field('description_xml', [])
            self.add_field('description_type', [])
            self.add_field('description_lang', [])
            self.add_field('description_narrative', [])
            self.add_field('description_narrative_lang', [])
            self.add_field('description_narrative_text', [])

            for description in description_all:
                self.add_value_list(
                    'description',
                    JSONRenderer().render(
                        DescriptionSerializer(description).data
                    ).decode()
                )
                self.add_value_list(
                    'description_xml',
                    DescriptionReference(description=description).to_string()
                )
                self.add_value_list('description_type', description.type_id)

                self.related_narrative(
                    description,
                    'description_narrative',
                    'description_narrative_text',
                    'description_lang'
                )

    def participating_org(self):
        participating_organisation_all = \
            self.record.participating_organisations.all()
        if participating_organisation_all:
            self.add_field('participating_org', [])
            self.add_field('participating_org_xml', [])
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
                        ParticipatingOrganisationSerializer(
                            participating_organisation
                        ).data
                    ).decode()
                )
                self.add_value_list(
                    'participating_org_xml',
                    ParticipatingOrgReference(
                        participating_org=participating_organisation
                    ).to_string()
                )

                self.add_value_list(
                    'participating_org_ref',
                    participating_organisation.ref
                )
                self.add_value_list(
                    'participating_org_type',
                    participating_organisation.type_id
                )
                self.add_value_list(
                    'participating_org_role',
                    participating_organisation.role_id
                )

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
            self.add_field('other_identifier_xml', [])
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
                self.add_field(
                    'other_identifier_xml',
                    OtherIdentifierReference(
                        other_identifier=other_identifier
                    ).to_string()
                )

                self.add_value_list(
                    'other_identifier_ref',
                    other_identifier.identifier
                )
                self.add_value_list(
                    'other_identifier_type',
                    other_identifier.type_id
                )
                self.add_value_list(
                    'other_identifier_owner_org_ref',
                    other_identifier.owner_ref
                )

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
            self.add_field('activity_date_xml', [])
            self.add_field('activity_date_type', [])
            self.add_field('activity_date_iso_date', [])

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
                self.add_value_list(
                    'activity_date_xml',
                    ActivityDateReference(
                        activity_date=activity_date
                    ).to_string()
                )

                self.add_value_list(
                    'activity_date_type',
                    activity_date.type_id
                )

                if activity_date.iso_date:
                    self.add_value_list(
                        'activity_date_iso_date',
                        activity_date.iso_date
                    )

                if activity_date.type_id == '1':
                    self.add_field(
                        'activity_date_start_planned',
                        str(activity_date.iso_date)
                    )
                    self.add_field(
                        'activity_date_start_planned_f',
                        activity_date.iso_date
                    )
                elif activity_date.type_id == '2':
                    self.add_field(
                        'activity_date_start_actual',
                        str(activity_date.iso_date)
                    )
                    self.add_field(
                        'activity_date_start_actual_f',
                        activity_date.iso_date
                    )
                elif activity_date.type_id == '3':
                    self.add_field(
                        'activity_date_end_planned',
                        str(activity_date.iso_date)
                    )
                    self.add_field(
                        'activity_date_end_planned_f',
                        activity_date.iso_date
                    )
                elif activity_date.type_id == '4':
                    self.add_field(
                        'activity_date_end_actual',
                        str(activity_date.iso_date)
                    )
                    self.add_field(
                        'activity_date_end_actual_f',
                        activity_date.iso_date
                    )

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
            self.add_field('contact_info_xml', [])

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
                self.add_value_list(
                    'contact_info_xml',
                    ContactInfoReference(
                        contact_info=contact_info
                    ).to_string()
                )

                self.add_value_list('contact_info_type', contact_info.type_id)
                self.add_value_list(
                    'contact_info_telephone',
                    contact_info.telephone
                )
                self.add_value_list('contact_info_email', contact_info.email)
                self.add_value_list(
                    'contact_info_website',
                    contact_info.website
                )

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
            self.add_field('recipient_country_xml', [])

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
                self.add_value_list(
                    'recipient_country_xml',
                    RecipientCountryReference(
                        recipient_country=recipient_country
                    ).to_string()
                )

                self.add_value_list(
                    'recipient_country_code',
                    recipient_country.country.code
                )
                self.add_value_list(
                    'recipient_country_name',
                    recipient_country.country.name
                )
                self.add_value_list(
                    'recipient_country_percentage',
                    decimal_string(recipient_country.percentage)
                )

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
            self.add_field('recipient_region_xml', [])

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
                        ActivityRecipientRegionSerializer(
                            recipient_region
                        ).data
                    ).decode()
                )
                self.add_value_list(
                    'recipient_region_xml',
                    RecipientRegionReference(
                        recipient_region=recipient_region
                    ).to_string()
                )

                self.add_value_list(
                    'recipient_region_code',
                    recipient_region.region.code
                )
                self.add_value_list(
                    'recipient_region_name',
                    recipient_region.region.name
                )
                self.add_value_list(
                    'recipient_region_vocabulary',
                    recipient_region.vocabulary.code
                )
                self.add_value_list(
                    'recipient_region_vocabulary_uri',
                    recipient_region.vocabulary_uri
                )
                self.add_value_list(
                    'recipient_region_percentage',
                    decimal_string(recipient_region.percentage)
                )

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
            self.add_field('location_xml', [])

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
                self.add_value_list(
                    'location_xml',
                    LocationReference(
                        location=location
                    ).to_string()
                )

                self.add_value_list('location_ref', location.ref)
                self.add_value_list(
                    'location_reach_code',
                    location.location_reach_id
                )
                self.add_value_list(
                    'location_id_vocabulary',
                    location.location_id_vocabulary_id
                )
                self.add_value_list(
                    'location_id_code', location.location_id_code
                )
                self.add_value_list(
                    'location_point_pos',
                    value_string(get_child_attr(location, 'point_pos.coords'))
                )
                self.add_value_list(
                    'location_exactness_code',
                    location.exactness_id
                )
                self.add_value_list(
                    'location_class_code',
                    location.location_class_id
                )
                self.add_value_list(
                    'location_feature_designation_code',
                    location.feature_designation_id
                )

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

                for location_administrative in \
                        location.locationadministrative_set.all():
                    self.add_value_list(
                        'location_administrative_vocabulary',
                        location_administrative.vocabulary.code
                    )
                    self.add_value_list(
                        'location_administrative_level',
                        location_administrative.level
                    )
                    self.add_value_list(
                        'location_administrative_code',
                        location_administrative.code
                    )

    def sector(self):
        activity_sector_all = self.record.activitysector_set.all()
        if activity_sector_all:
            self.add_field('sector', [])
            self.add_field('sector_xml', [])

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
                self.add_value_list(
                    'sector_xml',
                    SectorReference(
                        sector=activity_sector
                    ).to_string()
                )

                self.add_value_list(
                    'sector_vocabulary',
                    activity_sector.vocabulary_id
                )
                self.add_value_list(
                    'sector_vocabulary_uri',
                    activity_sector.vocabulary_uri
                )
                self.add_value_list(
                    'sector_code',
                    activity_sector.sector.code
                )
                self.add_value_list(
                    'sector_percentage',
                    decimal_string(activity_sector.percentage)
                )

                self.related_narrative(
                    activity_sector,
                    'sector_narrative',
                    'sector_narrative_text',
                    'sector_narrative_lang'
                )

    def tag(self):
        tag_all = self.record.activitytag_set.all()
        if tag_all:
            self.add_field('tag', [])
            self.add_field('tag_xml', [])
            self.add_field('tag_vocabulary', [])
            self.add_field('tag_vocabulary_uri', [])
            self.add_field('tag_code', [])

            self.add_field('tag_narrative', [])
            self.add_field('tag_narrative_lang', [])
            self.add_field('tag_narrative_text', [])

            for tag in tag_all:
                self.add_value_list(
                    'tag',
                    JSONRenderer().render(
                        ActivityTagSerializer(tag).data
                    ).decode()
                )
                self.add_value_list(
                    'tag_xml',
                    TagReference(
                        tag=tag
                    ).to_string()
                )

                self.add_value_list(
                    'tag_vocabulary',
                    tag.vocabulary_id
                )
                self.add_value_list(
                    'tag_vocabulary_uri',
                    tag.vocabulary_uri
                )
                self.add_value_list(
                    'tag_code',
                    tag.code
                )

                self.related_narrative(
                    tag,
                    'tag_narrative',
                    'tag_narrative_text',
                    'tag_narrative_lang'
                )

    def country_budget_items(self):
        country_budget_item = get_child_attr(
            self.record,
            'country_budget_items'
        )
        if country_budget_item:
            self.add_field(
                'country_budget_items',
                JSONRenderer().render(
                    CountryBudgetItemsSerializer(country_budget_item).data
                ).decode()
            )
            self.add_field(
                'country_budget_items_xml',
                CountryBudgetItemsReference(
                    country_budget_items=country_budget_item
                ).to_string()
            )

            self.add_field(
                'country_budget_items_vocabulary',
                country_budget_item.vocabulary_id
            )

            self.add_field('country_budget_items_budget_item_code', [])
            self.add_field('country_budget_items_budget_item_percentage', [])

            self.add_field(
                'country_budget_items_budget_description_narrative',
                []
            )
            self.add_field(
                'country_budget_items_budget_description_narrative_lang',
                []
            )
            self.add_field(
                'country_budget_items_budget_description_narrative_text',
                []
            )

            for budget_item in country_budget_item.budgetitem_set.all():
                self.add_value_list(
                    'country_budget_items_budget_item_code',
                    budget_item.code_id
                )
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
            self.add_field('humanitarian_scope_xml', [])

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
                self.add_field(
                    'humanitarian_scope_xml',
                    HumanitarianScopeReference(
                        humanitarian_scope=humanitarian_scope
                    ).to_string()
                )

                self.add_value_list(
                    'humanitarian_scope_type',
                    humanitarian_scope.type_id
                )
                self.add_value_list(
                    'humanitarian_scope_vocabulary',
                    humanitarian_scope.vocabulary_id
                )
                self.add_value_list(
                    'humanitarian_scope_vocabulary_uri',
                    humanitarian_scope.vocabulary_uri
                )
                self.add_value_list(
                    'humanitarian_scope_code',
                    humanitarian_scope.code
                )

                self.related_narrative(
                    humanitarian_scope,
                    'humanitarian_scope_narrative',
                    'humanitarian_scope_narrative_text',
                    'humanitarian_scope_narrative_lang'
                )

    def policy_marker(self):
        policy_marker_all = self.record.activitypolicymarker_set.all()
        if policy_marker_all:
            self.add_field('policy_marker', [])
            self.add_field('policy_marker_xml', [])

            self.add_field('policy_marker_vocabulary', [])
            self.add_field('policy_marker_vocabulary_uri', [])
            self.add_field('policy_marker_code', [])
            self.add_field('policy_marker_significance', [])

            self.add_field('policy_marker_narrative', [])
            self.add_field('policy_marker_narrative_lang', [])
            self.add_field('policy_marker_narrative_text', [])

            for policy_marker in policy_marker_all:
                self.add_value_list(
                    'policy_marker',
                    JSONRenderer().render(
                        ActivityPolicyMarkerSerializer(policy_marker).data
                    ).decode()
                )
                self.add_value_list(
                    'policy_marker_xml',
                    PolicyMarkerReference(
                        policy_marker=policy_marker
                    ).to_string()
                )

                self.add_value_list(
                    'policy_marker_vocabulary',
                    policy_marker.vocabulary_id
                )
                self.add_value_list(
                    'policy_marker_vocabulary_uri',
                    policy_marker.vocabulary_uri
                )
                self.add_value_list(
                    'policy_marker_code',
                    policy_marker.code_id
                )
                self.add_value_list(
                    'policy_marker_significance',
                    policy_marker.significance_id
                )

                self.related_narrative(
                    policy_marker,
                    'policy_marker_narrative',
                    'policy_marker_narrative_text',
                    'policy_marker_narrative_lang'
                )

    def default_aid_type(self):
        default_aid_type_all = self.record.default_aid_types.all()
        if default_aid_type_all:
            self.add_field('default_aid_type', [])
            self.add_field('default_aid_type_xml', [])
            self.add_field('default_aid_type_code', [])
            self.add_field('default_aid_type_vocabulary', [])

            for default_aid_type in default_aid_type_all:
                self.add_value_list(
                    'default_aid_type',
                    JSONRenderer().render(
                        ActivityDefaultAidTypeSerializer(
                            default_aid_type
                        ).data
                    ).decode()
                )
                self.add_value_list(
                    'default_aid_type_xml',
                    DefaultAidTypeReference(
                        default_aid_type=default_aid_type
                    ).to_string()
                )

                self.add_value_list(
                    'default_aid_type_code',
                    get_child_attr(
                        default_aid_type,
                        'aid_type.code'
                    )
                )
                self.add_value_list(
                    'default_aid_type_vocabulary',
                    get_child_attr(
                        default_aid_type,
                        'aid_type.vocabulary.code'
                    )
                )

    def budget(self):
        budget_all = self.record.budget_set.all()
        if budget_all:
            self.add_field('budget', [])
            self.add_field('budget_xml', [])
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
                self.add_value_list(
                    'budget_xml',
                    BudgetReference(budget=budget).to_string()
                )

                self.add_value_list('budget_type', budget.type_id)
                self.add_value_list('budget_status', budget.status_id)
                self.add_value_list(
                    'budget_period_start_iso_date',
                    date_string(budget.period_start)
                )
                self.add_value_list(
                    'budget_period_end_iso_date',
                    date_string(budget.period_end)
                )
                self.add_value_list(
                    'budget_value_currency',
                    budget.currency_id
                )
                self.add_value_list(
                    'budget_value_date',
                    date_string(budget.value_date)
                )
                self.add_value_list(
                    'budget_value',
                    decimal_string(budget.value)
                )

    def planned_disbursement(self):
        planned_disbursement_all = self.record.planneddisbursement_set.all()
        if planned_disbursement_all:
            self.add_field('planned_disbursement', [])
            self.add_field('planned_disbursement_xml', [])
            self.add_field('planned_disbursement_type', [])
            self.add_field('planned_disbursement_period_start_iso_date', [])
            self.add_field('planned_disbursement_period_end_iso_date', [])
            self.add_field('planned_disbursement_value_currency', [])
            self.add_field('planned_disbursement_value_date', [])
            self.add_field('planned_disbursement_value', [])
            self.add_field(
                'planned_disbursement_provider_org_provider_activity_id',
                []
            )
            self.add_field('planned_disbursement_provider_org_type', [])
            self.add_field('planned_disbursement_provider_org_ref', [])
            self.add_field('planned_disbursement_provider_org_narrative', [])
            self.add_field(
                'planned_disbursement_provider_org_narrative_lang',
                []
            )
            self.add_field(
                'planned_disbursement_provider_org_narrative_text',
                []
            )
            self.add_field(
                'planned_disbursement_receiver_org_provider_activity_id',
                []
            )
            self.add_field('planned_disbursement_receiver_org_type', [])
            self.add_field('planned_disbursement_receiver_org_ref', [])
            self.add_field('planned_disbursement_receiver_org_narrative', [])
            self.add_field(
                'planned_disbursement_receiver_org_narrative_lang',
                []
            )
            self.add_field(
                'planned_disbursement_receiver_org_narrative_text',
                []
            )

            for planned_disbursement in planned_disbursement_all:
                self.add_value_list(
                    'planned_disbursement',
                    JSONRenderer().render(
                        PlannedDisbursementSerializer(
                            planned_disbursement
                        ).data
                    ).decode()
                )
                self.add_value_list(
                    'planned_disbursement_xml',
                    PlannedDisbursementReference(
                        planned_disbursement=planned_disbursement
                    ).to_string()
                )

                self.add_value_list(
                    'planned_disbursement_type',
                    planned_disbursement.type_id
                )
                self.add_value_list(
                    'planned_disbursement_period_start_iso_date',
                    date_string(planned_disbursement.period_start)
                )
                self.add_value_list(
                    'planned_disbursement_period_end_iso_date',
                    date_string(planned_disbursement.period_end)
                )
                self.add_value_list(
                    'planned_disbursement_value_date',
                    date_string(planned_disbursement.value_date)
                )
                self.add_value_list(
                    'planned_disbursement_value_currency',
                    planned_disbursement.currency_id
                )
                self.add_value_list(
                    'planned_disbursement_value',
                    decimal_string(planned_disbursement.value)
                )

                self.add_value_list(
                    'planned_disbursement_provider_org_provider_activity_id',
                    get_child_attr(
                        planned_disbursement,
                        'provider_organisation.provider_activity_ref'
                    )
                )
                self.add_value_list(
                    'planned_disbursement_provider_org_type',
                    get_child_attr(
                        planned_disbursement,
                        'provider_organisation.type_id'
                    )
                )
                self.add_value_list(
                    'planned_disbursement_provider_org_ref',
                    get_child_attr(
                        planned_disbursement,
                        'provider_organisation.ref'
                    )
                )

                self.related_narrative(
                    get_child_attr(
                        planned_disbursement,
                        'provider_organisation'
                    ),
                    'planned_disbursement_provider_org_narrative',
                    'planned_disbursement_provider_org_narrative_text',
                    'planned_disbursement_provider_org_narrative_lang'
                )

    def transaction(self):
        transaction_all = self.record.transaction_set.all()
        if transaction_all:
            self.add_field('transaction', [])
            self.add_field('transaction_xml', [])
            self.add_field('transaction_ref', [])
            self.add_field('transaction_humanitarian', [])
            self.add_field('transaction_type', [])
            self.add_field('transaction_date_iso_date', [])
            self.add_field('transaction_value_currency', [])
            self.add_field('transaction_value_date', [])
            self.add_field('transaction_value', [])
            self.add_field('transaction_provider_org_provider_activity_id', [])
            self.add_field('transaction_provider_org_type', [])
            self.add_field('transaction_provider_org_ref', [])
            self.add_field('transaction_provider_org_narrative', [])
            self.add_field('transaction_provider_org_narrative_lang', [])
            self.add_field('transaction_provider_org_narrative_text', [])
            self.add_field('transaction_receiver_org_receiver_activity_id', [])
            self.add_field('transaction_receiver_org_type', [])
            self.add_field('transaction_receiver_org_ref', [])
            self.add_field('transaction_receiver_org_narrative', [])
            self.add_field('transaction_receiver_org_narrative_lang', [])
            self.add_field('transaction_receiver_org_narrative_text', [])
            self.add_field('transaction_disbursement_channel_code', [])
            self.add_field('transaction_sector_vocabulary', [])
            self.add_field('transaction_sector_vocabulary_uri', [])
            self.add_field('transaction_sector_code', [])
            self.add_field('transaction_recipient_country_code', [])
            self.add_field('transaction_recipient_region_code', [])
            self.add_field('transaction_recipient_region_vocabulary', [])
            self.add_field('transaction_flow_type_code', [])
            self.add_field('transaction_finance_type_code', [])
            self.add_field('transaction_aid_type_code', [])
            self.add_field('transaction_aid_type_vocabulary', [])
            self.add_field('transaction_tied_status_code', [])

            for transaction in transaction_all:
                self.add_value_list(
                    'transaction',
                    JSONRenderer().render(
                        TransactionSerializer(
                            instance=transaction,
                            fields=[
                                'id',
                                'activity_id',
                                'ref',
                                'humanitarian',
                                'transaction_type',
                                'transaction_date',
                                'value',
                                'value_date',
                                'currency',
                                'description',
                                'currency',
                                'description',
                                'provider_organisation',
                                'receiver_organisation',
                                'disbursement_channel',
                                'sector',
                                'recipient_country',
                                'recipient_region',
                                'flow_type',
                                'finance_type',
                                'aid_type',
                                'tied_status',
                                'sectors',
                                'iati_identifier',
                                'recipient_countries',
                                'recipient_regions',
                                'usd_value'
                            ]
                        ).data
                    ).decode()
                )
                self.add_value_list(
                    'transaction_xml',
                    TransactionReference(transaction=transaction).to_string()
                )

                self.add_value_list('transaction_ref', transaction.ref)
                self.add_value_list(
                    'transaction_humanitarian',
                    bool_string(transaction.humanitarian)
                )
                self.add_value_list(
                    'transaction_type',
                    value_string(transaction.transaction_type_id)
                )
                self.add_value_list(
                    'transaction_date_iso_date',
                    date_string(transaction.transaction_date)
                )
                self.add_value_list(
                    'transaction_value_currency',
                    transaction.currency_id
                )
                self.add_value_list(
                    'transaction_value_date',
                    date_string(transaction.value_date)
                )
                self.add_value_list(
                    'transaction_value',
                    decimal_string(transaction.value)
                )

                provider_organisation = get_child_attr(
                    transaction,
                    'provider_organisation'
                )
                if provider_organisation:
                    self.add_value_list(
                        'transaction_provider_org_provider_activity_id',
                        provider_organisation.provider_activity_ref
                    )
                    self.add_value_list(
                        'transaction_provider_org_type',
                        provider_organisation.type_id
                    )
                    self.add_value_list(
                        'transaction_provider_org_ref',
                        provider_organisation.ref
                    )

                    self.related_narrative(
                        provider_organisation,
                        'transaction_provider_org_narrative',
                        'transaction_provider_org_narrative_text',
                        'transaction_provider_org_narrative_lang'
                    )

                receiver_organisation = get_child_attr(
                    transaction,
                    'receiver_organisation'
                )
                if receiver_organisation:
                    self.add_value_list(
                        'transaction_receiver_org_receiver_activity_id',
                        receiver_organisation.receiver_activity_ref
                    )
                    self.add_value_list(
                        'transaction_receiver_org_type',
                        receiver_organisation.type_id
                    )
                    self.add_value_list(
                        'transaction_receiver_org_ref',
                        receiver_organisation.ref
                    )

                    self.related_narrative(
                        receiver_organisation,
                        'transaction_receiver_org_narrative',
                        'transaction_receiver_org_narrative_text',
                        'transaction_receiver_org_narrative_lang'
                    )

                self.add_value_list(
                    'transaction_disbursement_channel_code',
                    transaction.disbursement_channel_id
                )

                for transaction_sector in \
                        transaction.transactionsector_set.all():
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
                        transaction_sector.sector.code
                    )

                for transaction_recipient_country in \
                        transaction.transactionrecipientcountry_set.all():
                    self.add_value_list(
                        'transaction_recipient_country_code',
                        transaction_recipient_country.country_id
                    )

                for transaction_recipient_region in \
                        transaction.transactionrecipientregion_set.all():
                    self.add_value_list(
                        'transaction_recipient_region_code',
                        transaction_recipient_region.region_id
                    )
                    self.add_value_list(
                        'transaction_recipient_region_vocabulary',
                        transaction_recipient_region.vocabulary_id
                    )

                self.add_value_list(
                    'transaction_flow_type_code',
                    transaction.flow_type_id
                )
                self.add_value_list(
                    'transaction_finance_type_code',
                    transaction.finance_type_id
                )

                for transaction_aid_type in \
                        transaction.transactionaidtype_set.all():
                    self.add_value_list(
                        'transaction_aid_type_code',
                        transaction_aid_type.aid_type.code
                    )
                    self.add_value_list(
                        'transaction_aid_type_vocabulary',
                        transaction_aid_type.aid_type.vocabulary_id
                    )

                self.add_value_list(
                    'transaction_tied_status_code',
                    transaction.tied_status_id
                )

    def document_link(self):
        document_link_all = self.record.documentlink_set.filter(
            result_id__isnull=True,
            result_indicator_id__isnull=True,
            result_indicator_baseline_id__isnull=True,
            result_indicator_period_actual_id__isnull=True,
            result_indicator_period_target_id__isnull=True
        )
        if document_link_all:
            self.add_field('document_link', [])
            self.add_field('document_link_xml', [])
            self.add_field('document_link_format', [])
            self.add_field('document_link_url', [])
            self.add_field('document_link_title_narrative', [])
            self.add_field('document_link_title_narrative_lang', [])
            self.add_field('document_link_title_narrative_text', [])
            self.add_field('document_link_description_narrative', [])
            self.add_field('document_link_description_narrative_lang', [])
            self.add_field('document_link_description_narrative_text', [])
            self.add_field('document_link_category_code', [])
            self.add_field('document_link_language_code', [])
            self.add_field('document_link_document_date_iso_date', [])

            for document_link in document_link_all:
                self.add_value_list(
                    'document_link',
                    JSONRenderer().render(
                        DocumentLinkSerializer(
                            instance=document_link,
                            fields=[
                                'format',
                                'url',
                                'categories',
                                'languages',
                                'title',
                                'document_date',
                                'description'
                            ]
                        ).data
                    ).decode()
                )
                self.add_value_list(
                    'document_link_xml',
                    DocumentLinkReference(
                        document_link=document_link
                    ).to_string()
                )

                self.add_value_list(
                    'document_link_format',
                    document_link.file_format_id
                )
                self.add_value_list('document_link_url', document_link.url)
                self.add_value_list(
                    'document_link_document_date_iso_date',
                    date_string(document_link.iso_date)
                )

                self.related_narrative(
                    get_child_attr(document_link, 'documentlinktitle'),
                    'document_link_title_narrative',
                    'document_link_title_narrative_text',
                    'document_link_title_narrative_lang'
                )

                self.related_narrative(
                    get_child_attr(document_link, 'documentlinkdescription'),
                    'document_link_description_narrative',
                    'document_link_description_narrative_text',
                    'document_link_description_narrative_lang'
                )

                for document_link_category in \
                        document_link.documentlinkcategory_set.all():
                    self.add_value_list(
                        'document_link_category_code',
                        document_link_category.category_id
                    )

                for document_link_language in \
                        document_link.documentlinklanguage_set.all():
                    self.add_value_list(
                        'document_link_language_code',
                        document_link_language.language_id
                    )

    def related_activity(self):
        related_activity_all = self.record.relatedactivity_set.all()
        if related_activity_all:
            self.add_field('related_activity', [])
            self.add_field('related_activity_xml', [])
            self.add_field('related_activity_ref', [])
            self.add_field('related_activity_type', [])

            for related_activity in related_activity_all:
                self.add_value_list(
                    'related_activity',
                    JSONRenderer().render(
                        RelatedActivitySerializer(
                            instance=related_activity,
                            fields=[
                                'ref',
                                'type'
                            ]
                        ).data
                    ).decode()
                )
                self.add_value_list(
                    'related_activity_xml',
                    RelatedActivityReference(
                        related_activity=related_activity
                    ).to_string()
                )

                self.add_value_list(
                    'related_activity_ref',
                    related_activity.ref
                )
                self.add_value_list(
                    'related_activity_type',
                    related_activity.type_id
                )

    def legacy_data(self):
        legacy_data_all = self.record.legacydata_set.all()
        if legacy_data_all:
            self.add_field('legacy_data', [])
            self.add_field('legacy_data_xml', [])
            self.add_field('legacy_data_name', [])
            self.add_field('legacy_data_value', [])
            self.add_field('legacy_data_iati_equivalent', [])

            for legacy_data in legacy_data_all:
                self.add_value_list(
                    'legacy_data',
                    JSONRenderer().render(
                        LegacyDataSerializer(
                            instance=legacy_data
                        ).data
                    ).decode()
                )
                self.add_value_list(
                    'legacy_data_xml',
                    LegacyDataReference(
                        legacy_data=legacy_data
                    ).to_string()
                )

                self.add_value_list(
                    'legacy_data_name',
                    legacy_data.name
                )
                self.add_value_list(
                    'legacy_data_value',
                    legacy_data.value
                )
                self.add_value_list(
                    'legacy_data_iati_equivalent',
                    legacy_data.iati_equivalent
                )

    def conditions(self):
        activity_condition = get_child_attr(self.record, 'conditions')
        if activity_condition:
            self.add_field(
                'conditions',
                JSONRenderer().render(
                    ConditionsSerializer(activity_condition).data
                ).decode()
            )
            self.add_field(
                'conditions_xml',
                ConditionsReference(
                    conditions=activity_condition
                ).to_string()
            )

            self.add_field(
                'conditions_attached',
                bool_string(activity_condition.attached)
            )

            self.add_field('conditions_condition_type', [])

            self.add_field('conditions_condition_narrative', [])
            self.add_field('conditions_condition_narrative_lang', [])
            self.add_field('conditions_condition_narrative_text', [])

            for condition in activity_condition.condition_set.all():
                self.add_value_list(
                    'conditions_condition_type',
                    condition.type_id
                )

                self.related_narrative(
                    condition,
                    'conditions_condition_narrative',
                    'conditions_condition_narrative_text',
                    'conditions_condition_narrative_lang'
                )

    def result(self):
        result_all = self.record.result_set.all()
        if result_all:
            self.add_field('result', [])
            self.add_field('result_xml', [])
            self.add_field('result_type', [])
            self.add_field('result_aggregation_status', [])
            self.add_field('result_title_narrative', [])
            self.add_field('result_title_narrative_lang', [])
            self.add_field('result_title_narrative_text', [])
            self.add_field('result_description_narrative', [])
            self.add_field('result_description_narrative_lang', [])
            self.add_field('result_description_narrative_text', [])
            self.add_field('result_document_link_url', [])
            self.add_field('result_document_link_format', [])
            self.add_field('result_document_link_title_narrative', [])
            self.add_field('result_document_link_title_narrative_lang', [])
            self.add_field('result_document_link_title_narrative_text', [])
            self.add_field('result_document_link_description_narrative', [])
            self.add_field(
                'result_document_link_description_narrative_lang',
                []
            )
            self.add_field(
                'result_document_link_description_narrative_text',
                []
            )
            self.add_field('result_document_link_category_code', [])
            self.add_field('result_document_link_language_code', [])
            self.add_field('result_document_link_document_date_iso_date', [])
            self.add_field('result_reference_code', [])
            self.add_field('result_reference_vocabulary', [])
            self.add_field('result_reference_vocabulary_uri', [])
            self.add_field('result_indicator_measure', [])
            self.add_field('result_indicator_ascending', [])
            self.add_field('result_indicator_aggregation_status', [])
            self.add_field('result_indicator_title_narrative', [])
            self.add_field('result_indicator_title_narrative_lang', [])
            self.add_field('result_indicator_title_narrative_text', [])
            self.add_field('result_indicator_description_narrative', [])
            self.add_field('result_indicator_description_narrative_lang', [])
            self.add_field('result_indicator_description_narrative_text', [])
            self.add_field('result_indicator_document_link_url', [])
            self.add_field('result_indicator_document_link_format', [])
            self.add_field(
                'result_indicator_document_link_title_narrative',
                []
            )
            self.add_field(
                'result_indicator_document_link_title_narrative_lang',
                []
            )
            self.add_field(
                'result_indicator_document_link_title_narrative_text',
                []
            )
            self.add_field(
                'result_indicator_document_link_description_narrative',
                []
            )
            self.add_field(
                'result_indicator_document_link_description_narrative_lang',
                []
            )
            self.add_field(
                'result_indicator_document_link_description_narrative_text',
                []
            )
            self.add_field('result_indicator_document_link_category_code', [])
            self.add_field('result_indicator_document_link_language_code', [])
            self.add_field(
                'result_indicator_document_link_document_date_iso_date',
                []
            )
            self.add_field('result_indicator_reference_code', [])
            self.add_field('result_indicator_reference_vocabulary', [])
            self.add_field('result_indicator_reference_vocabulary_uri', [])
            self.add_field('result_indicator_baseline_year', [])
            self.add_field('result_indicator_baseline_iso_date', [])
            self.add_field('result_indicator_baseline_value', [])
            self.add_field('result_indicator_baseline_location_ref', [])
            self.add_field('result_indicator_baseline_dimension_name', [])
            self.add_field('result_indicator_baseline_dimension_value', [])
            self.add_field('result_indicator_baseline_comment_narrative', [])
            self.add_field(
                'result_indicator_baseline_comment_narrative_lang',
                []
            )
            self.add_field(
                'result_indicator_baseline_comment_narrative_text',
                []
            )
            self.add_field('result_indicator_baseline_document_link_url', [])
            self.add_field(
                'result_indicator_baseline_document_link_format', []
            )
            self.add_field('result_indicator_baseline_document_link_title', [])
            self.add_field(
                'result_indicator_baseline_document_link_title_narrative_lang',
                []
            )
            self.add_field(
                'result_indicator_baseline_document_link_title_narrative_text',
                []
            )
            self.add_field(
                'result_indicator_baseline_document_link_description',
                []
            )
            self.add_field(
                'result_indicator_baseline_document_link_description_lang',
                []
            )
            self.add_field(
                'result_indicator_baseline_document_link_description_text',
                []
            )
            self.add_field(
                'result_indicator_baseline_document_link_category_code',
                []
            )
            self.add_field(
                'result_indicator_baseline_document_link_language_code',
                []
            )
            self.add_field('result_indicator_baseline_document_link_document_date_iso_date', [])  # NOQA: E501
            self.add_field('result_indicator_period_period_start_iso_date', [])
            self.add_field('result_indicator_period_period_end_iso_date', [])
            self.add_field('result_indicator_period_target_value', [])
            self.add_field('result_indicator_period_target_location_ref', [])
            self.add_field('result_indicator_period_target_dimension_name', [])
            self.add_field(
                'result_indicator_period_target_dimension_value',
                []
            )
            self.add_field(
                'result_indicator_period_target_comment_narrative',
                []
            )
            self.add_field(
                'result_indicator_period_target_comment_narrative_lang',
                []
            )
            self.add_field(
                'result_indicator_period_target_comment_narrative_text',
                []
            )
            self.add_field(
                'result_indicator_period_target_document_link_url',
                []
            )
            self.add_field(
                'result_indicator_period_target_document_link_format',
                []
            )
            self.add_field(
                'result_indicator_period_target_document_link_title_narrative',
                []
            )
            self.add_field('result_indicator_period_target_document_link_title_narrative_lang', [])  # NOQA: E501
            self.add_field('result_indicator_period_target_document_link_title_narrative_text', [])  # NOQA: E501
            self.add_field('result_indicator_period_target_document_link_description_narrative', [])  # NOQA: E501
            self.add_field('result_indicator_period_target_document_link_description_narrative_lang', [])  # NOQA: E501
            self.add_field('result_indicator_period_target_document_link_description_narrative_text', [])  # NOQA: E501
            self.add_field(
                'result_indicator_period_target_document_link_category_code',
                []
            )
            self.add_field(
                'result_indicator_period_target_document_link_language_code',
                []
            )
            self.add_field('result_indicator_period_target_document_link_document_date_iso_date', [])  # NOQA: E501
            self.add_field('result_indicator_period_actual_value', [])
            self.add_field('result_indicator_period_actual_location_ref', [])
            self.add_field('result_indicator_period_actual_dimension_name', [])
            self.add_field(
                'result_indicator_period_actual_dimension_value',
                []
            )
            self.add_field(
                'result_indicator_period_actual_comment_narrative',
                []
            )
            self.add_field(
                'result_indicator_period_actual_comment_narrative_lang',
                []
            )
            self.add_field(
                'result_indicator_period_actual_comment_narrative_text',
                []
            )
            self.add_field(
                'result_indicator_period_actual_document_link_url',
                []
            )
            self.add_field(
                'result_indicator_period_actual_document_link_format',
                []
            )
            self.add_field(
                'result_indicator_period_actual_document_link_title_narrative',
                []
            )
            self.add_field('result_indicator_period_actual_document_link_title_narrative_lang', [])  # NOQA: E501
            self.add_field('result_indicator_period_actual_document_link_title_narrative_text', [])  # NOQA: E501
            self.add_field('result_indicator_period_actual_document_link_description_narrative', [])  # NOQA: E501
            self.add_field('result_indicator_period_actual_document_link_description_narrative_lang', [])  # NOQA: E501
            self.add_field('result_indicator_period_actual_document_link_description_narrative_text', [])  # NOQA: E501
            self.add_field(
                'result_indicator_period_actual_document_link_category_code',
                []
            )
            self.add_field(
                'result_indicator_period_actual_document_link_language_code',
                []
            )
            self.add_field('result_indicator_period_actual_document_link_document_date_iso_date', [])  # NOQA: E501

            for result in result_all:
                self.add_value_list(
                    'result',
                    JSONRenderer().render(
                        ResultSerializer(result).data
                    ).decode()
                )
                self.add_value_list(
                    'result_xml',
                    ResultReference(result=result).to_string()
                )

                self.add_value_list('result_type', result.type_id)
                self.add_value_list(
                    'result_aggregation_status',
                    bool_string(result.aggregation_status)
                )

                self.related_narrative(
                    get_child_attr(result, 'resulttitle'),
                    'result_title_narrative',
                    'result_title_narrative_text',
                    'result_title_narrative_lang'
                )

                self.related_narrative(
                    get_child_attr(result, 'resultdescription'),
                    'result_description_narrative',
                    'result_description_narrative_text',
                    'result_description_narrative_lang'
                )

                for document_link in result.documentlink_set.all():
                    self.add_value_list(
                        'result_document_link_url',
                        document_link.url
                    )
                    self.add_value_list(
                        'result_document_link_format',
                        document_link.file_format_id
                    )

                    self.related_narrative(
                        get_child_attr(document_link, 'documentlinktitle'),
                        'result_document_link_title_narrative',
                        'result_document_link_title_narrative_text',
                        'result_document_link_title_narrative_lang'
                    )

                    self.related_narrative(
                        get_child_attr(
                            document_link,
                            'documentlinkdescription'
                        ),
                        'result_document_link_description_narrative',
                        'result_document_link_description_narrative_text',
                        'result_document_link_description_narrative_lang'
                    )

                    for document_link_category in \
                            document_link.documentlinkcategory_set.all():
                        self.add_value_list(
                            'result_document_link_category_code',
                            document_link_category.category_id
                        )

                    for document_link_language in \
                            document_link.documentlinklanguage_set.all():
                        self.add_value_list(
                            'result_document_link_language_code',
                            document_link_language.language_id
                        )

                    self.add_value_list(
                        'result_document_link_document_date_iso_date',
                        date_string(document_link.iso_date)
                    )

                for result_reference in result.resultreference_set.all():
                    self.add_value_list(
                        'result_reference_code', result_reference.code
                    )
                    self.add_value_list(
                        'result_reference_vocabulary',
                        result_reference.vocabulary_id
                    )
                    self.add_value_list(
                        'result_reference_vocabulary_uri',
                        result_reference.vocabulary_uri
                    )

                for result_indicator in result.resultindicator_set.all():
                    self.add_value_list(
                        'result_indicator_measure',
                        result_indicator.measure_id
                    )
                    self.add_value_list(
                        'result_indicator_ascending',
                        bool_string(result_indicator.ascending)
                    )
                    self.add_value_list(
                        'result_indicator_aggregation_status',
                        bool_string(result_indicator.aggregation_status)
                    )

                    self.related_narrative(
                        get_child_attr(
                            result_indicator,
                            'resultindicatortitle'
                        ),
                        'result_indicator_title_narrative',
                        'result_indicator_title_narrative_text',
                        'result_indicator_title_narrative_lang'
                    )

                    self.related_narrative(
                        get_child_attr(
                            result_indicator,
                            'resultindicatordescription'
                        ),
                        'result_indicator_description_narrative',
                        'result_indicator_description_narrative_text',
                        'result_indicator_description_narrative_lang'
                    )

                    for result_indicator_document_link in result_indicator.result_indicator_document_links.all():  # NOQA: E501
                        self.add_value_list(
                            'result_indicator_document_link_url',
                            result_indicator_document_link.url
                        )
                        self.add_value_list(
                            'result_indicator_document_link_format',
                            result_indicator_document_link.file_format_id
                        )

                        self.related_narrative(get_child_attr(result_indicator_document_link, 'documentlinktitle'), 'result_indicator_document_link_title_narrative', 'result_indicator_document_link_title_narrative_text', 'result_indicator_document_link_title_narrative_lang')  # NOQA: E501
                        self.related_narrative(get_child_attr(result_indicator_document_link, 'documentlinkdescription'), 'result_indicator_document_link_description_narrative',  'result_indicator_document_link_description_narrative_text', 'result_indicator_document_link_description_narrative_lang')  # NOQA: E501

                        for document_link_category in result_indicator_document_link.documentlinkcategory_set.all():  # NOQA: E501
                            self.add_value_list(
                                'result_indicator_document_link_category_code',
                                document_link_category.category_id
                            )

                        for document_link_language in result_indicator_document_link.documentlinklanguage_set.all():  # NOQA: E501
                            self.add_value_list(
                                'result_indicator_document_link_language_code',
                                document_link_language.language_id
                            )

                        self.add_value_list(
                            'result_indicator_document_link_document_date_iso_date',  # NOQA: E501
                            date_string(result_indicator_document_link.iso_date)  # NOQA: E501
                        )

                    for result_indicator_reference in result_indicator.resultindicatorreference_set.all():  # NOQA: E501
                        self.add_value_list(
                            'result_indicator_reference_code',
                            result_indicator_reference.code
                        )
                        self.add_value_list(
                            'result_indicator_reference_vocabulary',
                            result_indicator_reference.vocabulary_id
                        )
                        self.add_value_list(
                            'result_indicator_reference_vocabulary_uri',
                            result_indicator_reference.indicator_uri
                        )

                    for result_indicator_baseline in result_indicator.resultindicatorbaseline_set.all():  # NOQA: E501
                        self.add_value_list(
                            'result_indicator_baseline_year',
                            result_indicator_baseline.year
                        )
                        self.add_value_list(
                            'result_indicator_baseline_iso_date',
                            date_string(result_indicator_baseline.iso_date)
                        )
                        self.add_value_list(
                            'result_indicator_baseline_value',
                            result_indicator_baseline.value
                        )

                        for result_indicator_baseline_location in \
                                result_indicator_baseline.location_set.all():
                            self.add_value_list(
                                'result_indicator_baseline_location_ref',
                                result_indicator_baseline_location.ref
                            )

                        for result_indicator_baseline_dimension in result_indicator_baseline.resultindicatorbaselinedimension_set.all():  # NOQA: E501
                            self.add_value_list(
                                'result_indicator_baseline_dimension_name',
                                result_indicator_baseline_dimension.name
                            )
                            self.add_value_list(
                                'result_indicator_baseline_dimension_value',
                                result_indicator_baseline_dimension.value
                            )

                        self.related_narrative(get_child_attr(result_indicator_baseline, 'resultindicatorbaselinecomment'), 'result_indicator_baseline_comment_narrative', 'result_indicator_baseline_comment_narrative_text', 'result_indicator_baseline_comment_narrative_lang')  # NOQA: E501

                        for result_indicator_baseline_document_link in result_indicator_baseline.baseline_document_links.all():  # NOQA: E501
                            self.add_value_list(
                                'result_indicator_baseline_document_link_url',
                                result_indicator_baseline_document_link.url
                            )
                            self.add_value_list('result_indicator_baseline_document_link_format',  result_indicator_baseline_document_link.file_format_id)  # NOQA: E501
                            self.related_narrative(get_child_attr(result_indicator_baseline_document_link, 'documentlinktitle'), 'result_indicator_baseline_document_link_title',  'result_indicator_baseline_document_link_title_narrative_text', 'result_indicator_baseline_document_link_title_narrative_lang')  # NOQA: E501
                            self.related_narrative(get_child_attr(result_indicator_baseline_document_link, 'documentlinkdescription'), 'result_indicator_baseline_document_link_description',  'result_indicator_baseline_document_link_description_text',  'result_indicator_baseline_document_link_description_lang')  # NOQA: E501

                            for document_link_category in result_indicator_baseline_document_link.documentlinkcategory_set.all():  # NOQA: E501
                                self.add_value_list('result_indicator_baseline_document_link_category_code', document_link_category.category_id)  # NOQA: E501

                            for document_link_language in result_indicator_baseline_document_link.documentlinklanguage_set.all():  # NOQA: E501
                                self.add_value_list('result_indicator_baseline_document_link_language_code', document_link_language.language_id)  # NOQA: E501

                            self.add_value_list('result_indicator_baseline_document_link_document_date_iso_date', date_string(result_indicator_baseline_document_link.iso_date))  # NOQA: E501

                    for result_period in \
                            result_indicator.resultindicatorperiod_set.all():
                        self.add_value_list(
                            'result_indicator_period_period_start_iso_date',
                            date_string(result_period.period_start)
                        )
                        self.add_value_list(
                            'result_indicator_period_period_end_iso_date',
                            date_string(result_period.period_end)
                        )

                        for result_period_target in \
                                result_period.targets.all():
                            self.add_value_list(
                                'result_indicator_period_target_value',
                                result_period_target.value
                            )

                            for result_period_target_location in result_period_target.resultindicatorperiodtargetlocation_set.all():  # NOQA: E501
                                self.add_value_list('result_indicator_period_target_location_ref', result_period_target_location.ref)  # NOQA: E501

                            for result_period_target_dimension in result_period_target.resultindicatorperiodtargetdimension_set.all():  # NOQA: E501
                                self.add_value_list('result_indicator_period_target_dimension_name', result_period_target_dimension.name)  # NOQA: E501
                                self.add_value_list('result_indicator_period_target_dimension_value', result_period_target_dimension.value)  # NOQA: E501

                            for result_period_target_comment in result_period_target.resultindicatorperiodtargetcomment_set.all():  # NOQA: E501
                                self.related_narrative(result_period_target_comment, 'result_indicator_period_target_comment_narrative', 'result_indicator_period_target_comment_narrative_text', 'result_indicator_period_target_comment_narrative_lang')  # NOQA: E501

                            for document_link in result_period_target.period_target_document_links.all():  # NOQA: E501
                                self.add_value_list(
                                    'result_indicator_period_target_document_link_url',  # NOQA: E501
                                    document_link.url
                                )
                                self.add_value_list(
                                    'result_indicator_period_target_document_link_format',  # NOQA: E501
                                    document_link.file_format_id
                                )

                                self.related_narrative(
                                    get_child_attr(
                                        document_link, 'documentlinktitle'
                                    ),
                                    'result_indicator_period_target_document_link_title_narrative',  # NOQA: E501
                                    'result_indicator_period_target_document_link_title_narrative_text',  # NOQA: E501
                                    'result_indicator_period_target_document_link_title_narrative_lang'  # NOQA: E501
                                )

                                self.related_narrative(
                                    get_child_attr(
                                        document_link,
                                        'documentlinkdescription'
                                    ),
                                    'result_indicator_period_target_document_link_description_narrative',  # NOQA: E501
                                    'result_indicator_period_target_document_link_description_narrative_text',  # NOQA: E501
                                    'result_indicator_period_target_document_link_description_narrative_lang'  # NOQA: E501
                                )

                                for document_link_category in document_link.documentlinkcategory_set.all():  # NOQA: E501
                                    self.add_value_list(
                                        'result_indicator_period_target_document_link_category_code',  # NOQA: E501
                                        document_link_category.category_id
                                    )

                                for document_link_language in document_link.documentlinklanguage_set.all():  # NOQA: E501
                                    self.add_value_list(
                                        'result_indicator_period_target_document_link_language_code',  # NOQA: E501
                                        document_link_language.language_id
                                    )

                                self.add_value_list(
                                    'result_indicator_period_target_document_link_document_date_iso_date',  # NOQA: E501
                                    date_string(document_link.iso_date)
                                )

                        for result_period_actual in \
                                result_period.actuals.all():
                            self.add_value_list(
                                'result_indicator_period_actual_value',
                                result_period_actual.value
                            )

                            for result_period_actual_location in result_period_actual.resultindicatorperiodactuallocation_set.all():  # NOQA: E501
                                self.add_value_list(
                                    'result_indicator_period_actual_location_ref',  # NOQA: E501
                                    result_period_actual_location.ref
                                )

                            for result_period_actual_dimension in result_period_actual.resultindicatorperiodactualdimension_set.all():  # NOQA: E501
                                self.add_value_list(
                                    'result_indicator_period_actual_dimension_name',  # NOQA: E501
                                    result_period_actual_dimension.name
                                )
                                self.add_value_list(
                                    'result_indicator_period_actual_dimension_value',  # NOQA: E501
                                    result_period_actual_dimension.value
                                )

                            for result_period_actual_comment in result_period_actual.resultindicatorperiodactualcomment_set.all():  # NOQA: E501
                                self.related_narrative(
                                    result_period_actual_comment,
                                    'result_indicator_period_actual_comment_narrative',  # NOQA: E501
                                    'result_indicator_period_actual_comment_narrative_text',  # NOQA: E501
                                    'result_indicator_period_actual_comment_narrative_lang'  # NOQA: E501
                                )

                            for document_link in result_period_actual.period_actual_document_links.all():  # NOQA: E501
                                self.add_value_list('result_indicator_period_actual_document_link_url', document_link.url)  # NOQA: E501
                                self.add_value_list('result_indicator_period_actual_document_link_format', document_link.file_format_id)  # NOQA: E501

                                self.related_narrative(get_child_attr(document_link, 'documentlinktitle'), 'result_indicator_period_actual_document_link_title_narrative', 'result_indicator_period_actual_document_link_title_narrative_text', 'result_indicator_period_actual_document_link_title_narrative_lang')  # NOQA: E501
                                self.related_narrative(get_child_attr(document_link, 'documentlinkdescription'), 'result_indicator_period_actual_document_link_description_narrative', 'result_indicator_period_actual_document_link_description_narrative_text', 'result_indicator_period_actual_document_link_description_narrative_lang')  # NOQA: E501

                                for document_link_category in document_link.documentlinkcategory_set.all():  # NOQA: E501
                                    self.add_value_list(
                                        'result_indicator_period_actual_document_link_category_code',  # NOQA: E501
                                        document_link_category.category_id
                                    )

                                for document_link_language in document_link.documentlinklanguage_set.all():  # NOQA: E501
                                    self.add_value_list(
                                        'result_indicator_period_actual_document_link_language_code',  # NOQA: E501
                                        document_link_language.language_id
                                    )

                                self.add_value_list(
                                    'result_indicator_period_actual_document_link_document_date_iso_date',  # NOQA: E501
                                    date_string(document_link.iso_date)
                                )

    def crs_add(self):
        crs_add_all = self.record.crsadd_set.all()
        if crs_add_all:
            self.add_field('crs_add', [])
            self.add_field('crs_add_xml', [])
            self.add_field('crs_add_other_flags_code', [])
            self.add_field('crs_add_other_flags_significance', [])
            self.add_field('crs_add_loan_terms_rate_1', [])
            self.add_field('crs_add_loan_terms_rate_2', [])
            self.add_field('crs_add_loan_terms_repayment_type_code', [])
            self.add_field('crs_add_loan_terms_repayment_plan_code', [])
            self.add_field('crs_add_loan_terms_commitment_date_iso_date', [])
            self.add_field('crs_add_loan_terms_repayment_first_date_iso_date', [])  # NOQA: E501
            self.add_field('crs_add_loan_terms_repayment_final_date_iso_date', [])  # NOQA: E501
            self.add_field('crs_add_loan_status_year', [])
            self.add_field('crs_add_loan_status_currency', [])
            self.add_field('crs_add_loan_status_value_date', [])
            self.add_field('crs_add_loan_status_interest_received', [])
            self.add_field('crs_add_loan_status_principal_outstanding', [])
            self.add_field('crs_add_loan_status_principal_arrears', [])
            self.add_field('crs_add_loan_status_interest_arrears', [])
            self.add_field('crs_add_channel_code', [])

            for crs_add in crs_add_all:
                self.add_value_list(
                    'crs_add',
                    JSONRenderer().render(
                        CrsAddSerializer(crs_add).data
                    ).decode()
                )
                self.add_value_list(
                    'crs_add_xml',
                    CrsAddReference(crs_add=crs_add).to_string()
                )

                self.add_value_list(
                    'crs_add_channel_code',
                    crs_add.channel_code_id
                )

                for crs_add_other_flag in crs_add.other_flags.all():
                    self.add_value_list(
                        'crs_add_other_flags_code',
                        crs_add_other_flag.other_flags_id
                    )
                    self.add_value_list(
                        'crs_add_other_flags_significance',
                        crs_add_other_flag.significance
                    )

                self.add_value_list(
                    'crs_add_loan_terms_rate_1',
                    value_string(
                        get_child_attr(
                            crs_add,
                            'loan_terms.rate_1'
                        )
                    )
                )
                self.add_value_list(
                    'crs_add_loan_terms_rate_2',
                    value_string(
                        get_child_attr(
                            crs_add,
                            'loan_terms.rate_2'
                        )
                    )
                )
                self.add_value_list(
                    'crs_add_loan_terms_repayment_type_code',
                    get_child_attr(
                        crs_add,
                        'loan_terms.repayment_type_id'
                    )
                )
                self.add_value_list(
                    'crs_add_loan_terms_repayment_plan_code',
                    get_child_attr(
                        crs_add,
                        'loan_terms.repayment_plan_id'
                    )
                )
                self.add_value_list(
                    'crs_add_loan_terms_commitment_date_iso_date',
                    date_string(
                        get_child_attr(
                            crs_add,
                            'loan_terms.commitment_date'
                        )
                    )
                )
                self.add_value_list(
                    'crs_add_loan_terms_repayment_first_date_iso_date',
                    date_string(
                        get_child_attr(
                            crs_add,
                            'loan_terms.repayment_first_date'
                        )
                    )
                )
                self.add_value_list(
                    'crs_add_loan_terms_repayment_final_date_iso_date',
                    date_string(
                        get_child_attr(
                            crs_add,
                            'loan_terms.repayment_final_date'
                        )
                    )
                )

                self.add_value_list(
                    'crs_add_loan_status_year',
                    get_child_attr(
                        crs_add, 'loan_status.year'
                    )
                )
                self.add_value_list(
                    'crs_add_loan_status_currency',
                    get_child_attr(
                        crs_add,
                        'loan_status.currency_id'
                    )
                )
                self.add_value_list(
                    'crs_add_loan_status_value_date',
                    value_string(
                        get_child_attr(
                            crs_add,
                            'loan_status.value_date'
                        )
                    )
                )
                self.add_value_list(
                    'crs_add_loan_status_interest_received',
                    value_string(
                        get_child_attr(
                            crs_add,
                            'loan_status.interest_received'
                        )
                    )
                )
                self.add_value_list(
                    'crs_add_loan_status_principal_outstanding',
                    value_string(
                        get_child_attr(
                            crs_add,
                            'loan_status.principal_outstanding'
                        )
                    )
                )
                self.add_value_list(
                    'crs_add_loan_status_principal_arrears',
                    get_child_attr(crs_add, 'loan_status.principal_arrears')
                )
                self.add_value_list(
                    'crs_add_loan_status_interest_arrears',
                    get_child_attr(crs_add, 'loan_status.interest_arrears')
                )

    def fss(self):
        fss_all = self.record.fss_set.all()
        if fss_all:
            self.add_field('fss', [])
            self.add_field('fss_xml', [])
            self.add_field('fss_extraction_date', [])
            self.add_field('fss_priority', [])
            self.add_field('fss_phaseout_year', [])
            self.add_field('fss_forecast_year', [])
            self.add_field('fss_forecast_value_date', [])
            self.add_field('fss_forecast_currency', [])
            self.add_field('fss_forecast_value', [])

            for fss in fss_all:
                self.add_value_list(
                    'fss',
                    JSONRenderer().render(FssSerializer(fss).data).decode()
                )
                self.add_value_list(
                    'fss_xml',
                    FssReference(
                        fss=fss
                    ).to_string()
                )

                self.add_value_list(
                    'fss_extraction_date',
                    value_string(fss.extraction_date)
                )
                self.add_value_list(
                    'fss_priority',
                    bool_string(fss.priority)
                )
                self.add_value_list(
                    'fss_phaseout_year',
                    value_string(fss.phaseout_year)
                )

                for forecast in fss.fssforecast_set.all():
                    self.add_value_list(
                        'fss_forecast_year',
                        value_string(forecast.year)
                    )
                    self.add_value_list(
                        'fss_forecast_value_date',
                        value_string(forecast.value_date)
                    )
                    self.add_value_list(
                        'fss_forecast_currency',
                        forecast.currency_id
                    )
                    self.add_value_list(
                        'fss_forecast_value',
                        value_string(forecast.value)
                    )

    def activity(self):
        activity = self.record

        self.add_field('id', value_string(activity.id))
        self.add_field('iati_identifier', activity.iati_identifier)
        self.add_field('last_updated_datetime', activity.last_updated_datetime)
        self.add_field(
            'last_updated_datetime_f',
            activity.last_updated_datetime
        )
        self.add_field('default_lang', activity.default_lang_id)
        self.add_field('default_currency', activity.default_currency_id)
        self.add_field('humanitarian', bool_string(activity.humanitarian))
        self.add_field('hierarchy', value_string(activity.hierarchy))
        self.add_field('linked_data_uri', activity.linked_data_uri)
        self.add_field(
            'activity_status_xml',
            ActivityStatusReference(
                activity_status=activity.activity_status
            ).to_string()
        )
        self.add_field('activity_status_code', activity.activity_status_id)

        if activity.scope:
            self.add_field(
                'activity_scope_xml',
                ActivityScopeReference(
                    activity_scope=activity.scope
                ).to_string()
            )
            self.add_field('activity_scope_code', activity.scope_id)

        self.add_field(
            'collaboration_type_code',
            activity.collaboration_type_id
        )
        if activity.collaboration_type:
            self.add_field(
                'collaboration_type_xml',
                CollaborationTypeReference(
                    collaboration_type=activity.collaboration_type
                ).to_string()
            )

        self.add_field('default_flow_type_code', activity.default_flow_type_id)
        if activity.default_flow_type_id:
            self.add_field(
                'default_flow_type_xml',
                DefaultFlowTypeReference(
                    default_flow_type=activity.default_flow_type
                ).to_string()
            )

        self.add_field(
            'default_finance_type_code',
            activity.default_finance_type_id
        )
        if activity.default_finance_type_id:
            self.add_field(
                'default_finance_type_xml',
                DefaultFinanceTypeReference(
                    default_finance_type=activity.default_finance_type
                ).to_string()
            )

        self.add_field(
            'default_tied_status_code',
            activity.default_tied_status_id
        )
        if activity.default_tied_status_id:
            self.add_field(
                'default_tied_status_xml',
                DefaultTiedStatusReference(
                    default_tied_status=activity.default_tied_status
                ).to_string()
            )

        self.add_field(
            'capital_spend_percentage',
            decimal_string(activity.capital_spend)
        )
        if activity.capital_spend:
            self.add_field(
                'capital_spend_xml',
                CapitalSpendReference(
                    capital_spend=activity.capital_spend
                ).to_string()
            )

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
        self.tag()
        self.country_budget_items()
        self.humanitarian_scope()
        self.policy_marker()
        self.default_aid_type()
        self.budget()
        self.planned_disbursement()
        self.transaction()
        self.document_link()
        self.related_activity()
        self.legacy_data()
        self.conditions()
        self.result()
        self.crs_add()
        self.fss()

    def to_representation(self, activity):
        self.record = activity

        self.indexing = {}
        self.representation = {}

        self.activity()
        self.build()

        return self.representation
