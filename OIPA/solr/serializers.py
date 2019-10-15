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


class ActivitySerializer(serializers.Serializer):

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
            str(activity.capital_spend) if activity.capital_spend > 0 else None,
            representation
        )

    def dataset(self, activity, representation):
        self.set_field('dataset_iati_version',  activity.iati_standard_version_id, representation)
        self.set_field('dataset_date_created', activity.dataset.date_created, representation)
        self.set_field('dataset_date_updated', activity.dataset.date_updated, representation)

    def reporting_org(self, activity, representation):
        reporting_org = activity.reporting_organisations.first()
        if reporting_org:
            self.set_field('reporting_org', json.dumps(ReportingOrgSerializer(reporting_org).data), representation)
            self.set_field('reporting_org_ref', reporting_org.ref, representation)
            self.set_field('reporting_org_type_code', reporting_org.type_id, representation)
            self.set_field('reporting_org_type_name', reporting_org.type.name, representation)
            self.set_field('reporting_org_secondary_reporter', '1' if reporting_org.secondary_reporter else '0', representation)
            self.set_field('reporting_org_narrative', reporting_org.organisation.primary_name, representation)

    def to_representation(self, activity):
        representation = OrderedDict()

        self.activity(activity=activity, representation=representation)
        self.dataset(activity=activity, representation=representation)
        self.reporting_org(activity=activity, representation=representation)

        return representation
