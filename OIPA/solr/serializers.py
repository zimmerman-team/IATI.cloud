import json
from collections import OrderedDict
from datetime import datetime
from rest_framework import serializers


class OrganisationTypeSerializer(serializers.Serializer):

    def set_value(self, value):
        return value

    def set_field(self, name, value, representation):
        if value:
            representation[name] = self.set_value(value)

    def reporting_org(self, organisation_type, representation):
        self.set_field('code', organisation_type.code, representation)
        self.set_field('name', organisation_type.name, representation)

    def to_representation(self, reporting_org):
        representation = OrderedDict()

        self.reporting_org(reporting_org, representation)

        return representation


class ReportingOrgSerializer(serializers.Serializer):

    def set_value(self, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")

        return value

    def set_field(self, name, value, representation):
        if value:
            representation[name] = self.set_value(value)

    def organisation_type(self, organisation_type, representation):
        if organisation_type:
            self.set_field('type', OrganisationTypeSerializer(organisation_type).data, representation)

    def reporting_org(self, reporting_org, representation):
        self.set_field('ref', reporting_org.ref, representation)
        self.set_field('secondary_reporter', '1' if reporting_org.secondary_reporter else '0', representation)
        self.set_field('narrative', reporting_org.organisation.primary_name, representation)

    def to_representation(self, reporting_org):
        representation = OrderedDict()

        self.reporting_org(reporting_org, representation)
        self.organisation_type(reporting_org.type, representation)

        return representation


class NarrativeSerializer(serializers.Serializer):

    def set_value(self, value):
        return value

    def set_field(self, name, value, representation):
        if value:
            representation[name] = self.set_value(value)

    def narrative(self, narrative, representation):
        self.set_field('lang', narrative.language.code, representation)
        self.set_field('text', narrative.content, representation)

    def to_representation(self, reporting_org):
        representation = OrderedDict()

        self.narrative(reporting_org, representation)

        return representation


class ParticipatingOrgSerializer(serializers.Serializer):

    def set_value(self, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")

        return value

    def set_field(self, name, value, representation):
        if value:
            representation[name] = self.set_value(value)

    def narrative(self, participating_org, representation):
        narratives_all = participating_org.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field('narrative', narratives, representation)

    def participating_org(self, participating_org, representation):
        self.set_field('ref', participating_org.ref, representation)
        self.set_field('role', participating_org.role_id, representation)
        self.set_field('type', participating_org.type_id, representation)

    def to_representation(self, participating_org):
        representation = OrderedDict()

        self.participating_org(participating_org, representation)
        self.narrative(participating_org, representation)

        return representation


class OtherIdentifierSerializer(serializers.Serializer):

    def set_value(self, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")

        return value

    def set_field(self, name, value, representation):
        if value:
            representation[name] = self.set_value(value)

    def narrative(self, other_identifier, representation):
        narratives_all = other_identifier.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field('narrative', narratives, representation)

    def other_identifier(self, other_identifier, representation):
        self.set_field('ref', other_identifier.identifier, representation)
        self.set_field('type', other_identifier.type_id, representation)
        self.set_field('owner_org_ref', other_identifier.owner_ref, representation)

    def to_representation(self, other_identifier):
        representation = OrderedDict()

        self.other_identifier(other_identifier, representation)
        self.narrative(other_identifier, representation)

        return representation


class ActivityDateSerializer(serializers.Serializer):

    def set_value(self, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")

        return value

    def set_field(self, name, value, representation):
        if value:
            representation[name] = self.set_value(value)

    def narrative(self, activity_date, representation):
        narratives_all = activity_date.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field('narrative', narratives, representation)

    def activity_date(self, activity_date, representation):
        self.set_field('type', activity_date.type_id, representation)
        self.set_field('iso_date', activity_date.iso_date.strftime("%Y-%m-%d"), representation)

    def to_representation(self, activity_date):
        representation = OrderedDict()

        self.activity_date(activity_date, representation)
        self.narrative(activity_date, representation)

        return representation


class ContactInfoSerializer(serializers.Serializer):

    def set_value(self, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")

        return value

    def set_field(self, name, value, representation):
        if value:
            representation[name] = self.set_value(value)

    def narrative(self, contact_info_item, representation, field_name='narrative'):
        narratives_all = contact_info_item.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field(field_name, narratives, representation)

    def contact_info(self, contact_info, representation):
        self.set_field('type', contact_info.type_id, representation)
        self.set_field('telephone', contact_info.telephone, representation)
        self.set_field('email', contact_info.email, representation)
        self.set_field('website', contact_info.website, representation)

    def to_representation(self, contact_info):
        representation = OrderedDict()

        self.contact_info(contact_info, representation)
        self.narrative(contact_info.organisation, representation, 'organisation')
        self.narrative(contact_info.department, representation, 'department')
        self.narrative(contact_info.person_name, representation, 'person_name')
        self.narrative(contact_info.job_title, representation, 'job_title')
        self.narrative(contact_info.mailing_address, representation, 'mailing_address')

        return representation


class ActivitySerializer(serializers.Serializer):

    def add_to_list(self, data_list, value):
        if value:
            data_list.append(value)

    def set_value(self, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")

        return value

    def set_field(self, name, value, representation):
        if value:
            representation[name] = self.set_value(value)

    def activity(self, activity, representation):
        self.set_field('id', str(activity.id), representation)
        self.set_field('iati_identifier', activity.iati_identifier, representation)
        self.set_field('default_lang', activity.default_lang_id, representation)
        self.set_field('default_currency', activity.default_currency_id, representation)
        self.set_field('humanitarian', '1' if activity.humanitarian else '0', representation)
        self.set_field('hierarchy', str(activity.hierarchy), representation)
        self.set_field('linked_data_uri', activity.linked_data_uri, representation)
        self.set_field('activity_status_code', activity.activity_status_id, representation)
        self.set_field('activity_scope_code', activity.scope_id, representation)
        self.set_field('collaboration_type_code', activity.collaboration_type_id, representation)
        self.set_field('default_flow_type_code', activity.default_flow_type_id, representation)
        self.set_field('default_finance_type_code', activity.default_finance_type_id, representation)
        self.set_field('default_tied_status_code', activity.default_tied_status_id, representation)
        self.set_field(
            'capital_spend_percentage',
            str(activity.capital_spend) if activity.capital_spend and activity.capital_spend > 0 else None,
            representation
        )

    def dataset(self, activity, representation):
        self.set_field('dataset_iati_version', activity.iati_standard_version_id, representation)
        self.set_field('dataset_date_created', activity.dataset.date_created, representation)
        self.set_field('dataset_date_updated', activity.dataset.date_updated, representation)

    def reporting_org(self, activity, representation):
        reporting_org = activity.reporting_organisations.first()
        if reporting_org:
            self.set_field('reporting_org', json.dumps(ReportingOrgSerializer(reporting_org).data), representation)
            self.set_field('reporting_org_ref', reporting_org.ref, representation)
            self.set_field('reporting_org_type_code', reporting_org.type_id, representation)
            self.set_field('reporting_org_type_name', reporting_org.type.name, representation)
            self.set_field(
                'reporting_org_secondary_reporter',
                '1' if reporting_org.secondary_reporter else '0',
                representation
            )
            self.set_field('reporting_org_narrative', reporting_org.organisation.primary_name, representation)

    def title(self, activity, representation):
        if activity.title:
            title = list()
            title_narrative_lang = list()
            title_narrative_text = list()

            for narrative in activity.title.narratives.all():
                if narrative.language:
                    title_narrative_lang.append(narrative.language.code)

                title_narrative_text.append(narrative.content)
                title.append(NarrativeSerializer(narrative).data)

            self.set_field('title', json.dumps(title), representation)
            self.set_field('title_narrative_lang', title_narrative_lang, representation)
            self.set_field('title_narrative_text', title_narrative_text, representation)

    def description(self, activity, representation):
        descriptions_all = activity.description_set.all()
        if descriptions_all:
            description_list = list()
            description_type = list()
            description_narrative_lang = list()
            description_narrative_text = list()

            for description in descriptions_all:
                for narrative in description.narratives.all():
                    description_type.append(description.type_id)

                    if narrative.language:
                        description_narrative_lang.append(narrative.language.code)

                    description_narrative_text.append(narrative.content)
                    description_list.append(NarrativeSerializer(narrative).data)

            self.set_field('description', json.dumps(description_list), representation)
            self.set_field('description_type', description_type, representation)
            self.set_field('description_narrative_lang', description_narrative_lang, representation)
            self.set_field('description_narrative_text', description_narrative_text, representation)

    def participating_org(self, activity, representation):
        participating_organisations_all = activity.participating_organisations.all()
        if participating_organisations_all:
            participating_org = list()
            participating_org_ref = list()
            participating_org_type = list()
            participating_org_role = list()
            participating_org_narrative = list()
            participating_org_narrative_lang = list()
            participating_org_narrative_text = list()

            for participating_organisation in participating_organisations_all:
                self.add_to_list(participating_org_ref, participating_organisation.ref)
                self.add_to_list(participating_org_type, participating_organisation.type_id)
                self.add_to_list(participating_org_role, participating_organisation.role_id)

                participating_org.append(ParticipatingOrgSerializer(participating_organisation).data)

                for narrative in participating_organisation.narratives.all():
                    participating_org_narrative.append(narrative.content)
                    participating_org_narrative_text.append(narrative.content)
                    if narrative.language:
                        participating_org_narrative_lang.append(narrative.language.code)

            self.set_field('participating_org', json.dumps(participating_org), representation)
            self.set_field('participating_org_ref', participating_org_ref, representation)
            self.set_field('participating_org_type', participating_org_type, representation)
            self.set_field('participating_org_role', participating_org_role, representation)
            self.set_field('participating_org_narrative', participating_org_narrative, representation)
            self.set_field('participating_org_narrative_lang', participating_org_narrative_lang, representation)
            self.set_field('participating_org_narrative_text', participating_org_narrative_text, representation)

    def other_identifier(self, activity, representation):
        other_identifiers_all = activity.otheridentifier_set.all()
        if other_identifiers_all:
            other_identifiers_list = list()
            other_identifier_ref = list()
            other_identifier_type = list()
            other_identifier_owner_org_ref = list()
            other_identifier_owner_org_narrative = list()
            other_identifier_owner_org_narrative_lang = list()
            other_identifier_owner_org_narrative_text = list()

            for other_identifier in other_identifiers_all:
                self.add_to_list(other_identifier_ref, other_identifier.identifier)
                self.add_to_list(other_identifier_type, other_identifier.type_id)
                self.add_to_list(other_identifier_owner_org_ref, other_identifier.owner_ref)

                other_identifiers_list.append(OtherIdentifierSerializer(other_identifier).data)

                for narrative in other_identifier.narratives.all():
                    other_identifier_owner_org_narrative.append(narrative.content)
                    other_identifier_owner_org_narrative_text.append(narrative.content)
                    if narrative.language:
                        other_identifier_owner_org_narrative_lang.append(narrative.language.code)

            self.set_field('other_identifier', json.dumps(other_identifiers_list), representation)
            self.set_field('other_identifier_ref', other_identifier_ref, representation)
            self.set_field('other_identifier_type', other_identifier_type, representation)
            self.set_field('other_identifier_owner_org_ref', other_identifier_owner_org_ref, representation)
            self.set_field(
                'other_identifier_owner_org_narrative',
                other_identifier_owner_org_narrative,
                representation
            )
            self.set_field(
                'other_identifier_owner_org_narrative_lang',
                other_identifier_owner_org_narrative_lang,
                representation
            )
            self.set_field(
                'other_identifier_owner_org_narrative_text',
                other_identifier_owner_org_narrative_text,
                representation
            )

    def activity_date(self, activity, representation):
        activity_dates_all = activity.activitydate_set.all()
        if activity_dates_all:
            activity_date_list = list()
            activity_date_type = list()
            activity_dates_iso_date = list()

            activity_date_start_planned = None
            activity_date_start_actual = None
            activity_date_end_planned = None
            activity_date_end_actual = None

            activity_date_narrative = list()
            activity_date_narrative_lang = list()
            activity_date_narrative_text = list()

            for activity_date in activity_dates_all:
                self.add_to_list(activity_date_type, activity_date.type_id)

                if activity_date.iso_date:
                    activity_dates_iso_date.append(activity_date.iso_date.strftime("%Y-%m-%d"))

                if activity_date.type_id == '1':
                    activity_date_start_planned = activity_date.iso_date.strftime("%Y-%m-%d")
                elif activity_date.type_id == '2':
                    activity_date_start_actual = activity_date.iso_date.strftime("%Y-%m-%d")
                elif activity_date.type_id == '3':
                    activity_date_end_planned = activity_date.iso_date.strftime("%Y-%m-%d")
                elif activity_date.type_id == '4':
                    activity_date_end_actual = activity_date.iso_date.strftime("%Y-%m-%d")

                activity_date_list.append(ActivityDateSerializer(activity_date).data)

                for narrative in activity_date.narratives.all():
                    activity_date_narrative.append(narrative.content)
                    activity_date_narrative_text.append(narrative.content)
                    if narrative.language:
                        activity_date_narrative_lang.append(narrative.language.code)

            self.set_field('activity_date', json.dumps(activity_date_list), representation)
            self.set_field('activity_date_type', activity_date_type, representation)
            self.set_field('activity_dates_iso_date', activity_dates_iso_date, representation)

            self.set_field('activity_date_start_planned', activity_date_start_planned, representation)
            self.set_field('activity_date_start_actual', activity_date_start_actual, representation)
            self.set_field('activity_date_end_planned', activity_date_end_planned, representation)
            self.set_field('activity_date_end_actual', activity_date_end_actual, representation)

            self.set_field('activity_date_narrative', activity_date_narrative, representation)
            self.set_field('activity_date_narrative_lang', activity_date_narrative_lang, representation)
            self.set_field('activity_date_narrative_text', activity_date_narrative_text, representation)

    def contact_info(self, activity, representation):
        contact_infos_all = activity.contactinfo_set.all()
        if contact_infos_all:
            contact_info_list = list()
            contact_info_type = list()

            contact_info_organisation_narrative = list()
            contact_info_organisation_narrative_lang = list()
            contact_info_organisation_narrative_text = list()

            contact_info_department_narrative = list()
            contact_info_department_narrative_lang = list()
            contact_info_department_narrative_text = list()

            contact_info_person_name_narrative = list()
            contact_info_person_name_narrative_lang = list()
            contact_info_person_name_narrative_text = list()

            contact_info_job_title_narrative = list()
            contact_info_job_title_narrative_lang = list()
            contact_info_job_title_narrative_text = list()

            contact_info_mailing_address_narrative = list()
            contact_info_mailing_address_narrative_lang = list()
            contact_info_mailing_address_narrative_text = list()

            contact_info_telephone = list()
            contact_info_email = list()
            contact_info_website = list()

            for contact_info in contact_infos_all:
                self.add_to_list(contact_info_type, contact_info.type_id)
                self.add_to_list(contact_info_telephone, contact_info.telephone)
                self.add_to_list(contact_info_email, contact_info.email)
                self.add_to_list(contact_info_website, contact_info.website)

                contact_info_list.append(ContactInfoSerializer(contact_info).data)

                for narrative in contact_info.organisation.narratives.all():
                    contact_info_organisation_narrative.append(narrative.content)
                    contact_info_organisation_narrative_text.append(narrative.content)
                    if narrative.language:
                        contact_info_organisation_narrative_lang.append(narrative.language.code)

                for narrative in contact_info.department.narratives.all():
                    contact_info_department_narrative.append(narrative.content)
                    contact_info_department_narrative_text.append(narrative.content)
                    if narrative.language:
                        contact_info_department_narrative_lang.append(narrative.language.code)

                for narrative in contact_info.person_name.narratives.all():
                    contact_info_person_name_narrative.append(narrative.content)
                    contact_info_person_name_narrative_text.append(narrative.content)
                    if narrative.language:
                        contact_info_person_name_narrative_lang.append(narrative.language.code)

                for narrative in contact_info.job_title.narratives.all():
                    contact_info_job_title_narrative.append(narrative.content)
                    contact_info_job_title_narrative_text.append(narrative.content)
                    if narrative.language:
                        contact_info_job_title_narrative_lang.append(narrative.language.code)

                for narrative in contact_info.mailing_address.narratives.all():
                    contact_info_mailing_address_narrative.append(narrative.content)
                    contact_info_mailing_address_narrative_text.append(narrative.content)
                    if narrative.language:
                        contact_info_mailing_address_narrative_lang.append(narrative.language.code)

            self.set_field('contact_info', json.dumps(contact_info_list), representation)

            self.set_field('contact_info_type', contact_info_type, representation)
            self.set_field('contact_info_telephone', contact_info_telephone, representation)
            self.set_field('contact_info_email', contact_info_email, representation)
            self.set_field('contact_info_website', contact_info_website, representation)

            self.set_field('contact_info_organisation_narrative', contact_info_organisation_narrative, representation)
            self.set_field(
                'contact_info_organisation_narrative_lang', contact_info_organisation_narrative_lang, representation
            )
            self.set_field(
                'contact_info_organisation_narrative_text', contact_info_organisation_narrative_text, representation
            )

            self.set_field('contact_info_department_narrative', contact_info_department_narrative, representation)
            self.set_field(
                'contact_info_department_narrative_lang', contact_info_department_narrative_lang, representation
            )
            self.set_field(
                'contact_info_department_narrative_text', contact_info_department_narrative_text, representation
            )

            self.set_field('contact_info_person_name_narrative', contact_info_person_name_narrative, representation)
            self.set_field(
                'contact_info_person_name_narrative_lang', contact_info_person_name_narrative_lang, representation
            )
            self.set_field(
                'contact_info_person_name_narrative_text', contact_info_person_name_narrative_text, representation
            )

            self.set_field('contact_info_job_title_narrative', contact_info_job_title_narrative, representation)
            self.set_field(
                'contact_info_job_title_narrative_lang', contact_info_job_title_narrative_lang, representation
            )
            self.set_field(
                'contact_info_job_title_narrative_text', contact_info_job_title_narrative_text, representation
            )

            self.set_field(
                'contact_info_mailing_address_narrative', contact_info_mailing_address_narrative, representation
            )
            self.set_field(
                'contact_info_mailing_address_narrative_lang',
                contact_info_mailing_address_narrative_lang,
                representation
            )
            self.set_field(
                'contact_info_mailing_address_narrative_text',
                contact_info_mailing_address_narrative_text,
                representation
            )

    def to_representation(self, activity):
        representation = OrderedDict()

        self.activity(activity=activity, representation=representation)
        self.dataset(activity=activity, representation=representation)
        self.reporting_org(activity=activity, representation=representation)
        self.title(activity=activity, representation=representation)
        self.description(activity=activity, representation=representation)
        self.participating_org(activity=activity, representation=representation)
        self.other_identifier(activity=activity, representation=representation)
        self.activity_date(activity=activity, representation=representation)
        self.contact_info(activity=activity, representation=representation)

        return representation
