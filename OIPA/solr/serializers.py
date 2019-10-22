import json
from collections import OrderedDict
from datetime import datetime
from rest_framework import serializers

from iati.models import CountryBudgetItem, PlannedDisbursementProvider, \
    PlannedDisbursementReceiver, Conditions, ResultTitle, ResultDescription, \
    DocumentLinkTitle, DocumentLinkDescription, ResultIndicatorTitle, \
    ResultIndicatorBaselineComment, CrsAddLoanTerms, CrsAddLoanStatus
from iati.transaction.models import TransactionProvider, TransactionReceiver


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


class RecipientCountrySerializer(serializers.Serializer):

    def set_value(self, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")

        return value

    def set_field(self, name, value, representation):
        if value:
            representation[name] = self.set_value(value)

    def narrative(self, recipient_country, representation):
        narratives_all = recipient_country.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field('narrative', narratives, representation)

    def recipient_country(self, recipient_country, representation):
        self.set_field('code', recipient_country.country.code, representation)
        self.set_field('name', recipient_country.country.name, representation)
        self.set_field(
            'percentage',
            str(recipient_country.percentage) if recipient_country.percentage > 0 else None,
            representation
        )

    def to_representation(self, recipient_country):
        representation = OrderedDict()

        self.recipient_country(recipient_country, representation)
        self.narrative(recipient_country, representation)

        return representation


class RecipientRegionSerializer(serializers.Serializer):

    def set_value(self, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")

        return value

    def set_field(self, name, value, representation):
        if value:
            representation[name] = self.set_value(value)

    def narrative(self, recipient_region, representation):
        narratives_all = recipient_region.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field('narrative', narratives, representation)

    def recipient_region(self, recipient_region, representation):
        self.set_field('code', recipient_region.region.code, representation)
        self.set_field('name', recipient_region.region.name, representation)
        self.set_field('vocabulary', recipient_region.vocabulary.code, representation)
        self.set_field('vocabulary_uri', recipient_region.vocabulary_uri, representation)
        self.set_field(
            'percentage',
            str(recipient_region.percentage) if recipient_region.percentage > 0 else None,
            representation
        )

    def to_representation(self, recipient_region):
        representation = OrderedDict()

        self.recipient_region(recipient_region, representation)
        self.narrative(recipient_region, representation)

        return representation


class AdministrativeSerializer(serializers.Serializer):

    def set_value(self, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")

        return value

    def set_field(self, name, value, representation):
        if value:
            representation[name] = self.set_value(value)

    def administrative(self, administrative, representation):
        self.set_field('vocabulary', administrative.vocabulary.code, representation)
        self.set_field('level', administrative.level, representation)
        self.set_field('code', administrative.code, representation)

    def to_representation(self, administrative):
        representation = OrderedDict()

        self.administrative(administrative, representation)

        return representation


class LocationSerializer(serializers.Serializer):

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

    def narrative(self, location_item, representation, field_name='narrative'):
        narratives_all = location_item.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field(field_name, narratives, representation)

    def location(self, location, representation):
        self.set_field('ref', location.ref, representation)
        self.set_field('location_reach_code', location.location_reach.code, representation)
        self.set_field('location_id_vocabulary', location.location_id_vocabulary.code, representation)
        self.set_field('location_id_code', location.location_id_code, representation)
        self.set_field('point_pos', str(location.point_pos.coords), representation)
        self.set_field('exactness_code', location.exactness.code, representation)
        self.set_field('location_class_code', location.location_class.code, representation)
        self.set_field('feature_designation_code', location.feature_designation.code, representation)

    def administrative(self, location, representation):
        administrative_all = location.locationadministrative_set.all()
        if administrative_all:
            administrative_list = list()
            for administrative in administrative_all:
                self.add_to_list(administrative_list, AdministrativeSerializer(administrative).data)

            self.set_field('administrative', administrative_list, representation)

    def to_representation(self, location):
        representation = OrderedDict()

        self.location(location, representation)
        self.narrative(location.name, representation, 'name')
        self.narrative(location.description, representation, 'description')
        self.narrative(location.activity_description, representation, 'activity_description')
        self.administrative(location, representation)

        return representation


class ActivitySectorSerializer(serializers.Serializer):

    def set_value(self, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")

        return value

    def set_field(self, name, value, representation):
        if value:
            representation[name] = self.set_value(value)

    def narrative(self, activity_sector, representation):
        narratives_all = activity_sector.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field('narrative', narratives, representation)

    def activity_sector(self, activity_sector, representation):
        self.set_field('vocabulary', activity_sector.vocabulary.code, representation)
        self.set_field('vocabulary_uri', activity_sector.vocabulary_uri, representation)
        self.set_field('code', activity_sector.sector.code, representation)
        self.set_field(
            'percentage',
            str(activity_sector.percentage) if activity_sector.percentage > 0 else None,
            representation
        )

    def to_representation(self, activity_sector):
        representation = OrderedDict()

        self.activity_sector(activity_sector, representation)
        self.narrative(activity_sector, representation)

        return representation


class BudgetItemSerializer(serializers.Serializer):

    def set_value(self, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")

        return value

    def set_field(self, name, value, representation):
        if value:
            representation[name] = self.set_value(value)

    def narrative(self, budget_item, representation, field_name='narrative'):
        narratives_all = budget_item.description.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field(field_name, narratives, representation)

    def budget_item(self, budget_item, representation):
        self.set_field('code', budget_item.code_id, representation)
        self.set_field(
            'percentage',
            str(budget_item.percentage) if budget_item.percentage > 0 else None,
            representation
        )

    def to_representation(self, budget_item):
        representation = OrderedDict()

        self.budget_item(budget_item, representation)
        self.narrative(budget_item, representation, 'description')

        return representation


class CountryBudgetItemsSerializer(serializers.Serializer):

    def set_value(self, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")

        return value

    def set_field(self, name, value, representation):
        if value:
            representation[name] = self.set_value(value)

    def country_budget_items(self, country_budget_items, representation):
        self.set_field('vocabulary', country_budget_items.vocabulary_id, representation)

    def budget_item(self, country_budget_items, representation):
        budget_item_all = country_budget_items.budgetitem_set.all()
        if budget_item_all:
            budget_item_list = list()
            for budget_item in budget_item_all:
                budget_item_list.append(BudgetItemSerializer(budget_item).data)

            self.set_field('budget_item', budget_item_list, representation)

    def to_representation(self, country_budget_items):
        representation = OrderedDict()

        self.country_budget_items(country_budget_items, representation)
        self.budget_item(country_budget_items, representation)

        return representation


class HumanitarianScopeSerializer(serializers.Serializer):

    def set_value(self, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")

        return value

    def set_field(self, name, value, representation):
        if value:
            representation[name] = self.set_value(value)

    def narrative(self, humanitarian_scope, representation):
        narratives_all = humanitarian_scope.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field('narrative', narratives, representation)

    def humanitarian_scope(self, humanitarian_scope, representation):
        self.set_field('type', humanitarian_scope.type_id, representation)
        self.set_field('vocabulary', humanitarian_scope.vocabulary_id, representation)
        self.set_field('vocabulary_uri', humanitarian_scope.vocabulary_uri, representation)
        self.set_field('code', humanitarian_scope.code, representation)

    def to_representation(self, humanitarian_scope):
        representation = OrderedDict()

        self.humanitarian_scope(humanitarian_scope, representation)
        self.narrative(humanitarian_scope, representation)

        return representation


class PolicyMarkerSerializer(serializers.Serializer):

    def set_value(self, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")

        return value

    def set_field(self, name, value, representation):
        if value:
            representation[name] = self.set_value(value)

    def narrative(self, policy_marker, representation):
        narratives_all = policy_marker.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field('narrative', narratives, representation)

    def policy_marker(self, policy_marker, representation):
        self.set_field('vocabulary', policy_marker.vocabulary_id, representation)
        self.set_field('vocabulary_uri', policy_marker.vocabulary_uri, representation)
        self.set_field('code', policy_marker.code_id, representation)
        self.set_field('significance', policy_marker.significance_id, representation)

    def to_representation(self, policy_marker):
        representation = OrderedDict()

        self.policy_marker(policy_marker, representation)
        self.narrative(policy_marker, representation)

        return representation


class BudgetSerializer(serializers.Serializer):

    def set_value(self, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")

        return value

    def set_field(self, name, value, representation):
        if value:
            representation[name] = self.set_value(value)

    def narrative(self, humanitarian_scope, representation):
        narratives_all = humanitarian_scope.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field('narrative', narratives, representation)

    def budget(self, budget, representation):
        self.set_field('type', budget.type_id, representation)
        self.set_field('status', budget.status_id, representation)
        self.set_field(
            'period_start',
            str(budget.period_start.strftime("%Y-%m-%d")) if budget.period_start else None,
            representation
        )
        self.set_field(
            'period_end',
            str(budget.period_end.strftime("%Y-%m-%d")) if budget.period_end else None,
            representation
        )
        self.set_field(
            'value_date',
            str(budget.value_date.strftime("%Y-%m-%d")) if budget.value_date else None,
            representation
        )
        self.set_field('currency', budget.currency_id, representation)
        self.set_field(
            'value',
            str(budget.value) if budget.value > 0 else None,
            representation
        )

    def to_representation(self, budget):
        representation = OrderedDict()

        self.budget(budget, representation)

        return representation


class ProviderOrgSerializer(serializers.Serializer):

    def set_value(self, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")

        return value

    def set_field(self, name, value, representation):
        if value:
            representation[name] = self.set_value(value)

    def narrative(self, provider_org, representation):
        narratives_all = provider_org.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field('narrative', narratives, representation)

    def provider_org(self, provider_org, representation):
        self.set_field('provider_activity_id', provider_org.provider_activity_ref, representation)
        self.set_field('type', provider_org.type_id, representation)
        self.set_field('ref', provider_org.ref, representation)

    def to_representation(self, provider_org):
        representation = OrderedDict()

        self.provider_org(provider_org, representation)
        self.narrative(provider_org, representation)

        return representation


class ReceiverOrgSerializer(serializers.Serializer):

    def set_value(self, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")

        return value

    def set_field(self, name, value, representation):
        if value:
            representation[name] = self.set_value(value)

    def narrative(self, receiver_org, representation):
        narratives_all = receiver_org.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field('narrative', narratives, representation)

    def receiver_org(self, receiver_org, representation):
        self.set_field('receiver_activity_id', receiver_org.receiver_activity_ref, representation)
        self.set_field('type', receiver_org.type_id, representation)
        self.set_field('ref', receiver_org.ref, representation)

    def to_representation(self, provider_org):
        representation = OrderedDict()

        self.receiver_org(provider_org, representation)
        self.narrative(provider_org, representation)

        return representation


class PlannedDisbursementSerializer(serializers.Serializer):

    def set_value(self, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")

        return value

    def set_field(self, name, value, representation):
        if value:
            representation[name] = self.set_value(value)

    def narrative(self, humanitarian_scope, representation):
        narratives_all = humanitarian_scope.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field('narrative', narratives, representation)

    def provider_org(self, planned_disbursement, representation):
        try:
            self.set_field(
                'provider_org',
                ProviderOrgSerializer(planned_disbursement.provider_organisation).data,
                representation
            )
        except PlannedDisbursementProvider.DoesNotExist:
            pass

    def receiver_org(self, planned_disbursement, representation):
        try:
            self.set_field(
                'receiver_org',
                ReceiverOrgSerializer(planned_disbursement.receiver_organisation).data,
                representation
            )
        except PlannedDisbursementReceiver.DoesNotExist:
            pass

    def planned_disbursement(self, planned_disbursement, representation):
        self.set_field('type', planned_disbursement.type_id, representation)
        self.set_field(
            'period_start',
            str(planned_disbursement.period_start.strftime(
                "%Y-%m-%d")) if planned_disbursement.period_start else None,
            representation
        )
        self.set_field(
            'period_end',
            str(planned_disbursement.period_end.strftime(
                "%Y-%m-%d")) if planned_disbursement.period_end else None,
            representation
        )
        self.set_field(
            'value_date',
            str(planned_disbursement.value_date.strftime(
                "%Y-%m-%d")) if planned_disbursement.value_date else None,
            representation
        )
        self.set_field('value_currency', planned_disbursement.currency_id, representation)
        self.set_field(
            'value',
            str(planned_disbursement.value) if planned_disbursement.value > 0 else None,
            representation
        )

    def to_representation(self, planned_disbursement):
        representation = OrderedDict()

        self.planned_disbursement(planned_disbursement, representation)
        self.provider_org(planned_disbursement, representation)
        self.receiver_org(planned_disbursement, representation)

        return representation


class AidTypeSerializer(serializers.Serializer):

    def set_value(self, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")

        return value

    def set_field(self, name, value, representation):
        if value:
            representation[name] = self.set_value(value)

    def narrative(self, receiver_org, representation):
        narratives_all = receiver_org.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field('narrative', narratives, representation)

    def aid_type(self, aid_type, representation):
        self.set_field('code', aid_type.code, representation)
        self.set_field('vocabulary', aid_type.vocabulary_id, representation)

    def to_representation(self, aid_type):
        representation = OrderedDict()

        self.aid_type(aid_type, representation)

        return representation


class TransactionSectorSerializer(serializers.Serializer):

    def set_value(self, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")

        return value

    def set_field(self, name, value, representation):
        if value:
            representation[name] = self.set_value(value)

    def narrative(self, transaction_sector, representation):
        narratives_all = transaction_sector.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field('narrative', narratives, representation)

    def transaction_sector(self, transaction_sector, representation):
        self.set_field('code', transaction_sector.sector_id, representation)
        self.set_field('vocabulary', transaction_sector.vocabulary_id, representation)
        self.set_field('vocabulary_uri', transaction_sector.vocabulary_uri, representation)

    def to_representation(self, transaction_sector):
        representation = OrderedDict()

        self.transaction_sector(transaction_sector, representation)
        self.narrative(transaction_sector, representation)

        return representation


class TransactionSerializer(serializers.Serializer):

    def set_value(self, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")

        return value

    def set_field(self, name, value, representation):
        if value:
            representation[name] = self.set_value(value)

    def narrative(self, humanitarian_scope, representation):
        narratives_all = humanitarian_scope.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field('narrative', narratives, representation)

    def aid_type(self, transaction, representation):
        transaction_aid_type_all = transaction.transactionaidtype_set.all()
        if transaction_aid_type_all:
            aid_type_list = list()
            for transaction_aid_type in transaction_aid_type_all:
                aid_type_list.append(AidTypeSerializer(transaction_aid_type.aid_type).data)

            self.set_field(
                'aid_type',
                aid_type_list,
                representation
            )

    def provider_org(self, transaction, representation):
        try:
            self.set_field(
                'provider_org',
                ProviderOrgSerializer(transaction.provider_organisation).data,
                representation
            )
        except TransactionProvider.DoesNotExist:
            pass

    def receiver_org(self, transaction, representation):
        try:
            self.set_field(
                'receiver_org',
                ReceiverOrgSerializer(transaction.receiver_organisation).data,
                representation
            )
        except TransactionReceiver.DoesNotExist:
            pass

    def recipient_country(self, transaction, representation):
        recipient_country_all = transaction.transactionrecipientcountry_set.all()
        if recipient_country_all:
            recipient_country_list = list()
            for recipient_country in recipient_country_all:
                recipient_country_list.append(RecipientCountrySerializer(recipient_country).data)

            self.set_field('recipient_country', recipient_country_list, representation)

    def recipient_region(self, transaction, representation):
        recipient_region_all = transaction.transactionrecipientregion_set.all()
        if recipient_region_all:
            recipient_region_list = list()
            for recipient_region in recipient_region_all:
                recipient_region_list.append(RecipientRegionSerializer(recipient_region).data)

            self.set_field('recipient_region', recipient_region_list, representation)

    def sector(self, transaction, representation):
        transaction_sector_all = transaction.transactionsector_set.all()
        if transaction_sector_all:
            transaction_sector_list = list()
            for transaction_sector in transaction_sector_all:
                transaction_sector_list.append(TransactionSectorSerializer(transaction_sector).data)

            self.set_field('sector', transaction_sector_list, representation)

    def transaction(self, transaction, representation):
        self.set_field('ref', transaction.ref, representation)
        self.set_field('humanitarian', '1' if transaction.humanitarian else '0', representation)
        self.set_field('transaction_type_code', transaction.transaction_type_id, representation)
        self.set_field(
            'transaction_date_iso_date',
            str(transaction.transaction_date.strftime("%Y-%m-%d")) if transaction.transaction_date else None,
            representation
        )
        self.set_field('disbursement_channel_code', transaction.disbursement_channel_id, representation)
        self.set_field('flow_type_code', transaction.flow_type_id, representation)
        self.set_field('tied_status_code', transaction.tied_status_id, representation)
        self.set_field('value_currency', transaction.currency_id, representation)
        self.set_field(
            'value_date',
            str(transaction.value_date.strftime("%Y-%m-%d")) if transaction.value_date else None,
            representation
        )
        self.set_field(
            'value',
            str(transaction.value) if transaction.value > 0 else None,
            representation
        )

    def to_representation(self, transaction):
        representation = OrderedDict()

        self.transaction(transaction, representation)
        self.provider_org(transaction, representation)
        self.receiver_org(transaction, representation)
        self.aid_type(transaction, representation)
        self.sector(transaction, representation)
        self.recipient_country(transaction, representation)
        self.recipient_region(transaction, representation)

        return representation


class DocumentLinkSerializer(serializers.Serializer):

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

    def narrative(self, receiver_org, representation, field_name='narrative'):
        narratives_all = receiver_org.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field(field_name, narratives, representation)

    def document_link(self, document_link, representation):
        self.set_field('format', document_link.file_format_id, representation)
        self.set_field('url', document_link.url, representation)
        self.set_field(
            'document_date_iso_date',
            str(document_link.iso_date.strftime(
                "%Y-%m-%d")) if document_link.iso_date else None,
            representation
        )

    def category(self, document_link, representation):
        document_link_category_all = document_link.documentlinkcategory_set.all()
        if document_link_category_all:
            category_list = list()
            for document_link_category in document_link_category_all:
                self.add_to_list(
                    category_list,
                    document_link_category.category_id
                )

            self.set_field(
                'category_code',
                category_list,
                representation
            )

    def language(self, document_link, representation):
        document_link_language_all = document_link.documentlinklanguage_set.all()
        if document_link_language_all:
            language_list = list()
            for document_link_language in document_link_language_all:
                self.add_to_list(
                    language_list,
                    document_link_language.language_id
                )

            self.set_field(
                'language_code',
                language_list,
                representation
            )

    def to_representation(self, document_link):
        representation = OrderedDict()

        self.document_link(document_link, representation)
        self.narrative(document_link.documentlinktitle, representation, 'title')
        self.narrative(document_link.documentlinkdescription, representation, 'description')
        self.category(document_link, representation)
        self.language(document_link, representation)

        return representation


class ConditionSerializer(serializers.Serializer):

    def set_value(self, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")

        return value

    def set_field(self, name, value, representation):
        if value:
            representation[name] = self.set_value(value)

    def narrative(self, condition, representation):
        narratives_all = condition.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field('narrative', narratives, representation)

    def condition(self, condition, representation):
        self.set_field('type', condition.type_id, representation)

    def to_representation(self, condition):
        representation = OrderedDict()

        self.condition(condition, representation)
        self.narrative(condition, representation)

        return representation


class ConditionsSerializer(serializers.Serializer):

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

    def narrative(self, transaction_sector, representation):
        narratives_all = transaction_sector.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field('narrative', narratives, representation)

    def condition(self, conditions, representation):
        condition_all = conditions.condition_set.all()
        if condition_all:
            condition_list = list()
            for condition in condition_all:
                self.add_to_list(condition_list, ConditionSerializer(condition).data)

            self.set_field('condition', condition_list, representation)

    def conditions(self, conditions, representation):
        self.set_field('attached', '1' if conditions.attached else '0', representation)

    def to_representation(self, conditions):
        representation = OrderedDict()

        self.conditions(conditions, representation)
        self.condition(conditions, representation)

        return representation


class ReferenceSerializer(serializers.Serializer):

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

    def narrative(self, transaction_sector, representation):
        narratives_all = transaction_sector.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field('narrative', narratives, representation)

    def reference(self, reference, representation):
        self.set_field('code', reference.code, representation)
        self.set_field('vocabulary', reference.vocabulary_id, representation)
        self.set_field('vocabulary_uri', reference.vocabulary_uri, representation)

    def to_representation(self, reference):
        representation = OrderedDict()

        self.reference(reference, representation)

        return representation


class IndicatorReferenceSerializer(serializers.Serializer):

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

    def narrative(self, transaction_sector, representation):
        narratives_all = transaction_sector.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field('narrative', narratives, representation)

    def reference(self, reference, representation):
        self.set_field('code', reference.code, representation)
        self.set_field('vocabulary', reference.vocabulary_id, representation)
        self.set_field('vocabulary_uri', reference.indicator_uri, representation)

    def to_representation(self, reference):
        representation = OrderedDict()

        self.reference(reference, representation)

        return representation


class ResultLocationSerializer(serializers.Serializer):

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

    def narrative(self, transaction_sector, representation):
        narratives_all = transaction_sector.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field('narrative', narratives, representation)

    def location(self, location, representation):
        self.set_field('ref', location.ref, representation)

    def to_representation(self, reference):
        representation = OrderedDict()

        self.location(reference, representation)

        return representation


class DimensionSerializer(serializers.Serializer):

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

    def narrative(self, transaction_sector, representation):
        narratives_all = transaction_sector.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field('narrative', narratives, representation)

    def dimension(self, dimension, representation):
        self.set_field('name', dimension.name, representation)
        self.set_field('value', dimension.value, representation)

    def to_representation(self, dimension):
        representation = OrderedDict()

        self.dimension(dimension, representation)

        return representation


class BaselineSerializer(serializers.Serializer):

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

    def narrative(self, field, representation, field_name='narrative'):
        narratives_all = field.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field(field_name, narratives, representation)

    def baseline(self, baseline, representation):
        self.set_field('year', baseline.year, representation)
        self.set_field(
            'iso_date',
            str(baseline.iso_date.strftime(
                "%Y-%m-%d")) if baseline.iso_date else None,
            representation
        )
        self.set_field('value', baseline.value, representation)

    def location(self, baseline, representation):
        location_all = baseline.location_set.all()
        if location_all:
            location_list = list()

            for location in location_all:
                location_list.append(ResultLocationSerializer(location).data)

            self.set_field('location', location_list, representation)

    def dimension(self, baseline, representation):
        dimension_all = baseline.resultindicatorbaselinedimension_set.all()
        if dimension_all:
            dimension_list = list()

            for dimension in dimension_all:
                dimension_list.append(DimensionSerializer(dimension).data)

            self.set_field('dimension', dimension_list, representation)

    def comment(self, baseline, representation):
        try:
            self.narrative(baseline.resultindicatorbaselinecomment, representation, 'comment')
        except ResultIndicatorBaselineComment.DoesNotExist:
            pass

    def document_link(self, baseline, representation):
        document_link_all = baseline.baseline_document_links.all()
        if document_link_all:
            document_link_list = list()

            for document_link in document_link_all:
                document_link_list.append(
                    DocumentLinkSerializer(document_link).data
                )

            self.set_field('document_link', document_link_list, representation)

    def to_representation(self, baseline):
        representation = OrderedDict()

        self.baseline(baseline, representation)
        self.location(baseline, representation)
        self.dimension(baseline, representation)
        self.comment(baseline, representation)
        self.document_link(baseline, representation)

        return representation


class TargetSerializer(serializers.Serializer):

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

    def narrative(self, field, representation, field_name='narrative'):
        narratives_all = field.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field(field_name, narratives, representation)

    def location(self, item, representation):
        location_all = item.resultindicatorperiodtargetlocation_set.all()
        if location_all:
            location_list = list()

            for location in location_all:
                location_list.append(ResultLocationSerializer(location).data)

            self.set_field('location', location_list, representation)

    def dimension(self, item, representation):
        dimension_all = item.resultindicatorperiodtargetdimension_set.all()
        if dimension_all:
            dimension_list = list()

            for dimension in dimension_all:
                dimension_list.append(DimensionSerializer(dimension).data)

            self.set_field('dimension', dimension_list, representation)

    def comment(self, item, representation):
        self.narrative(item.resultindicatorperiodtargetcomment_set.first(), representation, 'comment')

    def document_link(self, target, representation):
        document_link_all = target.period_target_document_links.all()
        if document_link_all:
            document_link_list = list()

            for document_link in document_link_all:
                document_link_list.append(
                    DocumentLinkSerializer(document_link).data
                )

            self.set_field('document_link', document_link_list, representation)

    def to_representation(self, target):
        representation = OrderedDict()

        self.location(target, representation)
        self.dimension(target, representation)
        self.comment(target, representation)
        self.comment(target, representation)
        self.document_link(target, representation)

        return representation


class ActualSerializer(serializers.Serializer):

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

    def narrative(self, field, representation, field_name='narrative'):
        narratives_all = field.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field(field_name, narratives, representation)

    def location(self, item, representation):
        location_all = item.resultindicatorperiodactuallocation_set.all()
        if location_all:
            location_list = list()

            for location in location_all:
                location_list.append(ResultLocationSerializer(location).data)

            self.set_field('location', location_list, representation)

    def dimension(self, item, representation):
        dimension_all = item.resultindicatorperiodactualdimension_set.all()
        if dimension_all:
            dimension_list = list()

            for dimension in dimension_all:
                dimension_list.append(DimensionSerializer(dimension).data)

            self.set_field('dimension', dimension_list, representation)

    def comment(self, item, representation):
        self.narrative(item.resultindicatorperiodactualcomment_set.first(), representation, 'comment')

    def document_link(self, target, representation):
        document_link_all = target.period_actual_document_links.all()
        if document_link_all:
            document_link_list = list()

            for document_link in document_link_all:
                document_link_list.append(
                    DocumentLinkSerializer(document_link).data
                )

            self.set_field('document_link', document_link_list, representation)

    def to_representation(self, actual):
        representation = OrderedDict()

        self.location(actual, representation)
        self.dimension(actual, representation)
        self.comment(actual, representation)
        self.comment(actual, representation)
        self.document_link(actual, representation)

        return representation


class PeriodSerializer(serializers.Serializer):

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

    def narrative(self, field, representation, field_name='narrative'):
        narratives_all = field.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field(field_name, narratives, representation)

    def period(self, period, representation):
        self.set_field(
            'period_start',
            str(period.period_start.strftime(
                "%Y-%m-%d")) if period.period_start else None,
            representation
        )
        self.set_field(
            'period_end',
            str(period.period_end.strftime(
                "%Y-%m-%d")) if period.period_end else None,
            representation
        )

    def target(self, item, representation):
        target_all = item.targets.all()
        if target_all:
            target_list = list()

            for target in target_all:
                target_list.append(TargetSerializer(target).data)

            self.set_field('target', target_list, representation)

    def actual(self, item, representation):
        actual_all = item.actuals.all()
        if actual_all:
            target_list = list()

            for actual in actual_all:
                target_list.append(ActualSerializer(actual).data)

            self.set_field('actual', target_list, representation)

    def to_representation(self, period):
        representation = OrderedDict()

        self.period(period, representation)
        self.target(period, representation)
        self.actual(period, representation)

        return representation


class IndicatorSerializer(serializers.Serializer):

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

    def narrative(self, transaction_sector, representation, field_name='narrative'):
        narratives_all = transaction_sector.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field(field_name, narratives, representation)

    def indicator(self, indicator, representation):
        self.set_field('measure', indicator.measure_id, representation)
        self.set_field('ascending', '1' if indicator.ascending else '0', representation)
        self.set_field('aggregation_status', '1' if indicator.aggregation_status else '0', representation)

    def title(self, indicator, representation):
        try:
            self.narrative(indicator.resultindicatortitle, representation, 'title')
        except ResultIndicatorTitle.DoesNotExist:
            pass

    def description(self, indicator, representation):
        try:
            self.narrative(indicator.resultindicatordescription, representation, 'description')
        except ResultIndicatorTitle.DoesNotExist:
            pass

    def document_link(self, indicator, representation):
        document_link_all = indicator.result_indicator_document_links.all()
        if document_link_all:
            document_link_list = list()

            for document_link in document_link_all:
                document_link_list.append(
                    DocumentLinkSerializer(document_link).data
                )

            self.set_field('document_link', document_link_list, representation)

    def reference(self, indicator, representation):
        reference_all = indicator.resultindicatorreference_set.all()
        if reference_all:
            reference_list = list()

            for reference in reference_all:
                reference_list.append(IndicatorReferenceSerializer(reference).data)

            self.set_field('reference', reference_list, representation)

    def baseline(self, indicator, representation):
        baseline_all = indicator.resultindicatorbaseline_set.all()
        if baseline_all:
            baseline_list = list()

            for baseline in baseline_all:
                baseline_list.append(BaselineSerializer(baseline).data)

            self.set_field('baseline', baseline_list, representation)

    def period(self, indicator, representation):
        period_all = indicator.resultindicatorperiod_set.all()
        if period_all:
            period_list = list()

            for period in period_all:
                period_list.append(PeriodSerializer(period).data)

            self.set_field('period', period_list, representation)

    def to_representation(self, indicator):
        representation = OrderedDict()

        self.indicator(indicator, representation)
        self.title(indicator, representation)
        self.description(indicator, representation)
        self.document_link(indicator, representation)
        self.reference(indicator, representation)
        self.baseline(indicator, representation)
        self.period(indicator, representation)

        return representation


class ResultSerializer(serializers.Serializer):

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

    def narrative(self, item, representation, field_name='narrative'):
        narratives_all = item.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field(field_name, narratives, representation)

    def result(self, result, representation):
        self.set_field('type', result.type_id, representation)
        self.set_field(
            'aggregation_status',
            '1' if result.aggregation_status else '0',
            representation
        )

    def title(self, result, representation):
        try:
            self.narrative(result.resulttitle, representation, 'title')
        except ResultTitle.DoesNotExist:
            pass

    def description(self, result, representation):
        try:
            self.narrative(result.resultdescription, representation, 'description')
        except ResultTitle.DoesNotExist:
            pass

    def document_link(self, result, representation):
        document_link_all = result.documentlink_set.all()
        if document_link_all:
            document_link_list = list()

            for document_link in document_link_all:
                document_link_list.append(
                    DocumentLinkSerializer(document_link).data
                )

            self.set_field('document_link', document_link_list, representation)

    def reference(self, result, representation):
        reference_all = result.resultreference_set.all()
        if reference_all:
            reference_list = list()

            for reference in reference_all:
                reference_list.append(ReferenceSerializer(reference).data)

            self.set_field('reference', reference_list, representation)

    def indicator(self, result, representation):
        indicator_all = result.resultindicator_set.all()
        if indicator_all:
            indicator_list = list()

            for indicator in indicator_all:
                indicator_list.append(IndicatorSerializer(indicator).data)

            self.set_field('indicator', indicator_list, representation)

    def to_representation(self, result):
        representation = OrderedDict()

        self.result(result, representation)
        self.title(result, representation)
        self.description(result, representation)
        self.document_link(result, representation)
        self.reference(result, representation)
        self.indicator(result, representation)

        return representation


class OtherFlagSerializer(serializers.Serializer):

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

    def narrative(self, item, representation, field_name='narrative'):
        narratives_all = item.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field(field_name, narratives, representation)

    def other_flag(self, other_flag, representation):
        self.set_field('code', other_flag.other_flags_id, representation)
        self.set_field('significance', '1' if other_flag.significance else '0', representation)

    def to_representation(self, other_flag):
        representation = OrderedDict()

        self.other_flag(other_flag, representation)

        return representation


class LoanTermsSerializer(serializers.Serializer):

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

    def narrative(self, item, representation, field_name='narrative'):
        narratives_all = item.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field(field_name, narratives, representation)

    def loan_terms(self, loan_terms, representation):
        self.set_field('rate_1', str(loan_terms.rate_1), representation)
        self.set_field('rate_2', str(loan_terms.rate_2), representation)
        self.set_field('repayment_type_code', loan_terms.repayment_type_id, representation)
        self.set_field('repayment_plan_code', loan_terms.repayment_plan_id, representation)
        self.set_field('commitment_date', str(loan_terms.commitment_date.strftime(
            "%Y-%m-%d")) if loan_terms.commitment_date else None, representation)
        self.set_field('repayment_first_date', str(loan_terms.repayment_first_date.strftime(
            "%Y-%m-%d")) if loan_terms.repayment_first_date else None, representation)
        self.set_field('repayment_final_date', str(loan_terms.repayment_final_date.strftime(
            "%Y-%m-%d")) if loan_terms.repayment_final_date else None, representation)

    def to_representation(self, loan_terms):
        representation = OrderedDict()

        self.loan_terms(loan_terms, representation)

        return representation


class LoanStatusSerializer(serializers.Serializer):

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

    def narrative(self, item, representation, field_name='narrative'):
        narratives_all = item.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field(field_name, narratives, representation)

    def loan_terms(self, loan_status, representation):
        self.set_field('year', loan_status.year, representation)
        self.set_field('currency', loan_status.currency_id, representation)
        self.set_field('value_date', str(loan_status.value_date.strftime(
            "%Y-%m-%d")) if loan_status.value_date else None, representation)
        self.set_field('interest_received', str(loan_status.interest_received), representation)
        self.set_field('principal_outstanding', str(loan_status.principal_outstanding), representation)
        self.set_field('principal_arrears', str(loan_status.principal_arrears), representation)
        self.set_field('interest_arrears', str(loan_status.interest_arrears), representation)

    def to_representation(self, loan_terms):
        representation = OrderedDict()

        self.loan_terms(loan_terms, representation)

        return representation


class CrsAddSerializer(serializers.Serializer):

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

    def narrative(self, item, representation, field_name='narrative'):
        narratives_all = item.narratives.all()
        if narratives_all:
            narratives = list()
            for narrative in narratives_all:
                narratives.append(NarrativeSerializer(narrative).data)

            self.set_field(field_name, narratives, representation)

    def crs_add(self, crs_add, representation):
        self.set_field('channel_code', crs_add.channel_code_id, representation)

    def other_flag(self, crs_add, representation):
        other_flag_all = crs_add.other_flags.all()
        if other_flag_all:
            other_flag_list = list()

            for other_flag in other_flag_all:
                other_flag_list.append(OtherFlagSerializer(other_flag).data)

            self.set_field('other_flag', other_flag_list, representation)

    def loan_terms(self, crs_add, representation):
        try:
            self.set_field('loan_terms', LoanTermsSerializer(crs_add.loan_terms).data, representation)
        except CrsAddLoanTerms.DoesNotExist:
            pass

    def loan_status(self, crs_add, representation):
        try:
            self.set_field('loan_status', LoanStatusSerializer(crs_add.loan_status).data, representation)
        except CrsAddLoanStatus.DoesNotExist:
            pass

    def to_representation(self, crs_add):
        representation = OrderedDict()

        self.crs_add(crs_add, representation)
        self.other_flag(crs_add, representation)
        self.loan_terms(crs_add, representation)
        self.loan_status(crs_add, representation)

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
            title_narrative = list()
            title_narrative_lang = list()
            title_narrative_text = list()

            for narrative in activity.title.narratives.all():
                if narrative.language:
                    title_narrative_lang.append(narrative.language.code)

                title_narrative.append(narrative.content)
                title_narrative_text.append(narrative.content)
                title.append(NarrativeSerializer(narrative).data)

            self.set_field('title', json.dumps(title), representation)
            self.set_field('title_narrative', title_narrative, representation)
            self.set_field('title_narrative_lang', title_narrative_lang, representation)
            self.set_field('title_narrative_text', title_narrative_text, representation)

    def description(self, activity, representation):
        descriptions_all = activity.description_set.all()
        if descriptions_all:
            description_list = list()
            description_type = list()
            description_lang = list()
            description_narrative = list()
            description_narrative_lang = list()
            description_narrative_text = list()

            for description in descriptions_all:
                for narrative in description.narratives.all():
                    description_type.append(description.type_id)

                    if narrative.language:
                        description_lang.append(narrative.language.code)
                        description_narrative_lang.append(narrative.language.code)

                    description_narrative.append(narrative.content)
                    description_narrative_text.append(narrative.content)
                    description_list.append(NarrativeSerializer(narrative).data)

            self.set_field('description', json.dumps(description_list), representation)
            self.set_field('description_type', description_type, representation)
            self.set_field('description_lang', description_lang, representation)
            self.set_field('description_narrative', description_narrative, representation)
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

    def recipient_country(self, activity, representation):
        recipient_country_all = activity.activityrecipientcountry_set.all()
        if recipient_country_all:
            recipient_country_list = list()
            recipient_country_code = list()
            recipient_country_name = list()
            recipient_country_percentage = list()
            recipient_country_narrative = list()
            recipient_country_narrative_lang = list()
            recipient_country_narrative_text = list()

            for recipient_country in recipient_country_all:
                self.add_to_list(recipient_country_code, recipient_country.country.code)
                self.add_to_list(recipient_country_name, recipient_country.country.name)
                self.add_to_list(
                    recipient_country_percentage,
                    str(recipient_country.percentage) if recipient_country.percentage > 0 else None
                )

                recipient_country_list.append(RecipientCountrySerializer(recipient_country).data)

                for narrative in recipient_country.narratives.all():
                    recipient_country_narrative.append(narrative.content)
                    recipient_country_narrative_text.append(narrative.content)
                    if narrative.language:
                        recipient_country_narrative_lang.append(narrative.language.code)

            self.set_field('recipient_country', json.dumps(recipient_country_list), representation)
            self.set_field('recipient_country_code', recipient_country_code, representation)
            self.set_field('recipient_country_name', recipient_country_name, representation)
            self.set_field('recipient_country_percentage', recipient_country_percentage, representation)
            self.set_field('recipient_country_narrative', recipient_country_narrative, representation)
            self.set_field('recipient_country_narrative_lang', recipient_country_narrative_lang, representation)
            self.set_field('recipient_country_narrative_text', recipient_country_narrative_text, representation)

    def recipient_region(self, activity, representation):
        recipient_region_all = activity.activityrecipientregion_set.all()
        if recipient_region_all:
            recipient_region_list = list()
            recipient_region_code = list()
            recipient_region_name = list()
            recipient_region_vocabulary = list()
            recipient_region_vocabulary_uri = list()
            recipient_region_percentage = list()
            recipient_region_narrative = list()
            recipient_region_narrative_lang = list()
            recipient_region_narrative_text = list()

            for recipient_region in recipient_region_all:
                self.add_to_list(recipient_region_code, recipient_region.region.code)
                self.add_to_list(recipient_region_name, recipient_region.region.name)
                self.add_to_list(recipient_region_vocabulary, recipient_region.vocabulary.code)
                self.add_to_list(recipient_region_vocabulary_uri, recipient_region.vocabulary_uri)
                self.add_to_list(
                    recipient_region_percentage,
                    str(recipient_region.percentage) if recipient_region.percentage > 0 else None
                )

                recipient_region_list.append(RecipientRegionSerializer(recipient_region).data)

                for narrative in recipient_region.narratives.all():
                    recipient_region_narrative.append(narrative.content)
                    recipient_region_narrative_text.append(narrative.content)
                    if narrative.language:
                        recipient_region_narrative_lang.append(narrative.language.code)

            self.set_field('recipient_region', json.dumps(recipient_region_list), representation)
            self.set_field('recipient_region_code', recipient_region_code, representation)
            self.set_field('recipient_region_name', recipient_region_name, representation)
            self.set_field('recipient_region_vocabulary', recipient_region_vocabulary, representation)
            self.set_field('recipient_region_vocabulary_uri', recipient_region_vocabulary_uri, representation)
            self.set_field('recipient_region_percentage', recipient_region_percentage, representation)
            self.set_field('recipient_region_narrative', recipient_region_narrative, representation)
            self.set_field('recipient_region_narrative_lang', recipient_region_narrative_lang, representation)
            self.set_field('recipient_region_narrative_text', recipient_region_narrative_text, representation)

    def location(self, activity, representation):
        locations_all = activity.location_set.all()
        if locations_all:
            location_list = list()
            location_ref = list()
            location_reach_code = list()
            location_id_vocabulary = list()
            location_id_code = list()
            location_point_pos = list()
            location_exactness_code = list()
            location_class_code = list()
            location_feature_designation_code = list()

            location_name_narrative = list()
            location_name_narrative_lang = list()
            location_name_narrative_text = list()

            location_description_narrative = list()
            location_description_narrative_lang = list()
            location_description_narrative_text = list()

            location_activity_description_narrative = list()
            location_activity_description_narrative_lang = list()
            location_activity_description_narrative_text = list()

            location_administrative_vocabulary = list()
            location_administrative_level = list()
            location_administrative_code = list()

            for location in locations_all:
                self.add_to_list(location_ref, location.ref)
                self.add_to_list(location_reach_code, location.location_reach.code)
                self.add_to_list(location_id_vocabulary, location.location_id_vocabulary.code)
                self.add_to_list(location_id_code, location.location_id_code)
                self.add_to_list(location_point_pos, str(location.point_pos.coords))
                self.add_to_list(location_exactness_code, location.exactness.code)
                self.add_to_list(location_class_code, location.location_class.code)
                self.add_to_list(location_feature_designation_code, location.feature_designation.code)

                location_list.append(LocationSerializer(location).data)

                for narrative in location.name.narratives.all():
                    location_name_narrative.append(narrative.content)
                    location_name_narrative_text.append(narrative.content)
                    if narrative.language:
                        location_name_narrative_lang.append(narrative.language.code)

                for narrative in location.description.narratives.all():
                    location_description_narrative.append(narrative.content)
                    location_description_narrative_text.append(narrative.content)
                    if narrative.language:
                        location_description_narrative_lang.append(narrative.language.code)

                for narrative in location.activity_description.narratives.all():
                    location_activity_description_narrative.append(narrative.content)
                    location_activity_description_narrative_text.append(narrative.content)
                    if narrative.language:
                        location_activity_description_narrative_lang.append(narrative.language.code)

                for location_administrative in location.locationadministrative_set.all():
                    self.add_to_list(location_administrative_vocabulary, location_administrative.vocabulary.code)
                    self.add_to_list(location_administrative_level, location_administrative.level)
                    self.add_to_list(location_administrative_code, location_administrative.code)

            self.set_field('location', json.dumps(location_list), representation)

            self.set_field('location_ref', location_ref, representation)
            self.set_field('location_reach_code', location_reach_code, representation)
            self.set_field('location_id_vocabulary', location_id_vocabulary, representation)
            self.set_field('location_id_code', location_id_code, representation)
            self.set_field('location_point_pos', location_point_pos, representation)
            self.set_field('location_exactness_code', location_exactness_code, representation)
            self.set_field('location_class_code', location_class_code, representation)
            self.set_field('location_feature_designation_code', location_feature_designation_code, representation)

            self.set_field('location_name_narrative', location_name_narrative, representation)
            self.set_field('location_name_narrative_lang', location_name_narrative_lang, representation)
            self.set_field('location_name_narrative_text', location_name_narrative_text, representation)

            self.set_field('location_description_narrative', location_description_narrative, representation)
            self.set_field('location_name_narrative_lang', location_name_narrative_lang, representation)
            self.set_field('location_description_narrative_text', location_description_narrative_text, representation)

            self.set_field(
                'location_activity_description_narrative',
                location_activity_description_narrative,
                representation
            )
            self.set_field(
                'location_activity_description_narrative_lang',
                location_activity_description_narrative_lang,
                representation
            )
            self.set_field(
                'location_activity_description_narrative_text',
                location_activity_description_narrative_text,
                representation
            )

            self.set_field('location_administrative_vocabulary', location_administrative_vocabulary, representation)
            self.set_field('location_administrative_level', location_administrative_level, representation)
            self.set_field('location_administrative_code', location_administrative_code, representation)

    def sector(self, activity, representation):
        activity_sector_all = activity.activitysector_set.all()
        if activity_sector_all:
            sector_list = list()
            sector_vocabulary = list()
            sector_vocabulary_uri = list()
            sector_code = list()
            sector_percentage = list()
            sector_narrative = list()
            sector_narrative_lang = list()
            sector_narrative_text = list()

            for activity_sector in activity_sector_all:
                self.add_to_list(sector_vocabulary, activity_sector.vocabulary_id)
                self.add_to_list(sector_vocabulary_uri, activity_sector.vocabulary_uri)
                self.add_to_list(sector_code, activity_sector.sector.code)
                self.add_to_list(
                    sector_percentage,
                    str(activity_sector.percentage) if activity_sector.percentage > 0 else None
                )

                sector_list.append(ActivitySectorSerializer(activity_sector).data)

                for narrative in activity_sector.narratives.all():
                    sector_narrative.append(narrative.content)
                    sector_narrative_text.append(narrative.content)
                    if narrative.language:
                        sector_narrative_lang.append(narrative.language.code)

            self.set_field('sector', json.dumps(sector_list), representation)
            self.set_field('sector_vocabulary', sector_vocabulary, representation)
            self.set_field('sector_vocabulary_uri', sector_vocabulary_uri, representation)
            self.set_field('sector_code', sector_code, representation)
            self.set_field('sector_percentage', sector_percentage, representation)
            self.set_field('sector_narrative', sector_narrative, representation)
            self.set_field('sector_narrative_lang', sector_narrative_lang, representation)
            self.set_field('sector_narrative_text', sector_narrative_text, representation)

    def country_budget_items(self, activity, representation):
        try:
            country_budget_item = activity.country_budget_items

            country_budget_items_budget_item_code = list()
            country_budget_items_budget_item_percentage = list()

            country_budget_items_budget_description_narrative_lang = list()
            country_budget_items_budget_description_narrative_text = list()

            for budget_item in country_budget_item.budgetitem_set.all():
                self.add_to_list(country_budget_items_budget_item_code, budget_item.code_id)
                self.add_to_list(
                    country_budget_items_budget_item_percentage,
                    str(budget_item.percentage) if budget_item.percentage > 0 else None
                )

                for narrative in budget_item.description.narratives.all():
                    country_budget_items_budget_description_narrative_text.append(narrative.content)
                    if narrative.language:
                        country_budget_items_budget_description_narrative_lang.append(narrative.language.code)

            self.set_field(
                'country_budget_items',
                json.dumps(CountryBudgetItemsSerializer(country_budget_item).data),
                representation
            )
            self.set_field('country_budget_items_vocabulary', country_budget_item.vocabulary_id, representation)
            self.set_field(
                'country_budget_items_budget_item_code',
                country_budget_items_budget_item_code,
                representation
            )
            self.set_field(
                'country_budget_items_budget_item_percentage',
                country_budget_items_budget_item_percentage,
                representation
            )
            self.set_field(
                'country_budget_items_budget_description_narrative_lang',
                country_budget_items_budget_description_narrative_lang,
                representation
            )
            self.set_field(
                'country_budget_items_budget_description_narrative_text',
                country_budget_items_budget_description_narrative_text,
                representation
            )

        except CountryBudgetItem.DoesNotExist:
            pass

    def humanitarian_scope(self, activity, representation):
        humanitarian_scope_all = activity.humanitarianscope_set.all()
        if humanitarian_scope_all:
            humanitarian_scope_list = list()
            humanitarian_scope_type = list()
            humanitarian_scope_vocabulary = list()
            humanitarian_scope_vocabulary_uri = list()
            humanitarian_scope_code = list()

            humanitarian_scope_narrative = list()
            humanitarian_scope_narrative_lang = list()
            humanitarian_scope_narrative_text = list()

            for humanitarian_scope in humanitarian_scope_all:
                self.add_to_list(humanitarian_scope_type, humanitarian_scope.type_id)
                self.add_to_list(humanitarian_scope_vocabulary, humanitarian_scope.vocabulary_id)
                self.add_to_list(humanitarian_scope_vocabulary_uri, humanitarian_scope.vocabulary_uri)
                self.add_to_list(humanitarian_scope_code, humanitarian_scope.code)

                humanitarian_scope_list.append(HumanitarianScopeSerializer(humanitarian_scope).data)

                for narrative in humanitarian_scope.narratives.all():
                    humanitarian_scope_narrative.append(narrative.content)
                    humanitarian_scope_narrative_text.append(narrative.content)
                    if narrative.language:
                        humanitarian_scope_narrative_lang.append(narrative.language.code)

            self.set_field('humanitarian_scope', json.dumps(humanitarian_scope_list), representation)
            self.set_field('humanitarian_scope_type', humanitarian_scope_type, representation)
            self.set_field('humanitarian_scope_vocabulary', humanitarian_scope_vocabulary, representation)
            self.set_field('humanitarian_scope_vocabulary_uri', humanitarian_scope_vocabulary_uri, representation)
            self.set_field('humanitarian_scope_code', humanitarian_scope_code, representation)
            self.set_field('humanitarian_scope_narrative', humanitarian_scope_narrative, representation)
            self.set_field('humanitarian_scope_narrative_lang', humanitarian_scope_narrative_lang, representation)
            self.set_field('humanitarian_scope_narrative_text', humanitarian_scope_narrative_text, representation)

    def policy_marker(self, activity, representation):
        policy_marker_all = activity.activitypolicymarker_set.all()
        if policy_marker_all:
            policy_marker_list = list()
            policy_marker_vocabulary = list()
            policy_marker_vocabulary_uri = list()
            policy_marker_code = list()
            policy_marker_significance = list()
            policy_marker_narrative = list()
            policy_marker_narrative_lang = list()
            policy_marker_narrative_text = list()

            for policy_marker in policy_marker_all:
                self.add_to_list(policy_marker_vocabulary, policy_marker.vocabulary_id)
                self.add_to_list(policy_marker_vocabulary_uri, policy_marker.vocabulary_uri)
                self.add_to_list(policy_marker_code, policy_marker.code_id)
                self.add_to_list(policy_marker_significance, policy_marker.significance_id)

                policy_marker_list.append(PolicyMarkerSerializer(policy_marker).data)

                for narrative in policy_marker.narratives.all():
                    policy_marker_narrative.append(narrative.content)
                    policy_marker_narrative_text.append(narrative.content)
                    if narrative.language:
                        policy_marker_narrative_lang.append(narrative.language.code)

            self.set_field('policy_marker', json.dumps(policy_marker_list), representation)
            self.set_field('policy_marker_vocabulary', policy_marker_vocabulary, representation)
            self.set_field('policy_marker_vocabulary_uri', policy_marker_vocabulary_uri, representation)
            self.set_field('policy_marker_code', policy_marker_code, representation)
            self.set_field('policy_marker_significance', policy_marker_significance, representation)
            self.set_field('policy_marker_narrative', policy_marker_narrative, representation)
            self.set_field('policy_marker_narrative_lang', policy_marker_narrative_lang, representation)
            self.set_field('policy_marker_narrative_text', policy_marker_narrative_text, representation)

    def budget(self, activity, representation):
        budget_all = activity.budget_set.all()
        if budget_all:
            budget_list = list()
            budget_type = list()
            budget_status = list()
            budget_period_start_iso_date = list()
            budget_period_end_iso_date = list()
            budget_value_currency = list()
            budget_value_date = list()
            budget_value = list()

            for budget in budget_all:
                self.add_to_list(budget_type, budget.type_id)
                self.add_to_list(budget_status, budget.status_id)
                self.add_to_list(
                    budget_period_start_iso_date,
                    str(budget.period_start.strftime("%Y-%m-%d")) if budget.period_start else None
                )
                self.add_to_list(
                    budget_period_end_iso_date,
                    str(budget.period_end.strftime("%Y-%m-%d")) if budget.period_end else None
                )
                self.add_to_list(budget_value_currency, budget.currency_id)
                self.add_to_list(
                    budget_value_date,
                    str(budget.value_date.strftime("%Y-%m-%d")) if budget.value_date else None
                )
                self.add_to_list(
                    budget_value,
                    str(budget.value) if budget.value > 0 else None
                )

                budget_list.append(BudgetSerializer(budget).data)

            self.set_field('budget', json.dumps(budget_list) if budget_list else None, representation)
            self.set_field('budget_type', budget_type, representation)
            self.set_field('budget_status', budget_status, representation)
            self.set_field('budget_period_start_iso_date', budget_period_start_iso_date, representation)
            self.set_field('budget_period_end_iso_date', budget_period_end_iso_date, representation)
            self.set_field('budget_value_currency', budget_value_currency, representation)
            self.set_field('budget_value_date', budget_value_date, representation)
            self.set_field('budget_value', budget_value, representation)

    def planned_disbursement(self, activity, representation):
        planned_disbursement_all = activity.planneddisbursement_set.all()
        if planned_disbursement_all:
            planned_disbursement_list = list()
            planned_disbursement_type = list()
            planned_disbursement_period_start_iso_date = list()
            planned_disbursement_period_end_iso_date = list()
            planned_disbursement_value_currency = list()
            planned_disbursement_value_date = list()
            planned_disbursement_value = list()
            planned_disbursement_provider_org_provider_activity_id = list()
            planned_disbursement_provider_org_type = list()
            planned_disbursement_provider_org_ref = list()

            planned_disbursement_provider_org_narrative = list()
            planned_disbursement_provider_org_narrative_lang = list()
            planned_disbursement_provider_org_narrative_text = list()

            planned_disbursement_receiver_org_provider_activity_id = list()
            planned_disbursement_receiver_org_type = list()
            planned_disbursement_receiver_org_ref = list()

            planned_disbursement_receiver_org_narrative = list()
            planned_disbursement_receiver_org_narrative_lang = list()
            planned_disbursement_receiver_org_narrative_text = list()

            for planned_disbursement in planned_disbursement_all:
                self.add_to_list(planned_disbursement_type, planned_disbursement.type_id)
                self.add_to_list(
                    planned_disbursement_period_start_iso_date,
                    str(planned_disbursement.period_start.strftime(
                        "%Y-%m-%d")) if planned_disbursement.period_start else None
                )
                self.add_to_list(
                    planned_disbursement_period_end_iso_date,
                    str(planned_disbursement.period_end.strftime(
                        "%Y-%m-%d")) if planned_disbursement.period_end else None
                )
                self.add_to_list(
                    planned_disbursement_value_date,
                    str(planned_disbursement.value_date.strftime(
                        "%Y-%m-%d")) if planned_disbursement.value_date else None
                )
                self.add_to_list(planned_disbursement_value_currency, planned_disbursement.currency_id)
                self.add_to_list(
                    planned_disbursement_value,
                    str(planned_disbursement.value) if planned_disbursement.value > 0 else None
                )

                planned_disbursement_list.append(PlannedDisbursementSerializer(planned_disbursement).data)

                try:
                    self.add_to_list(
                        planned_disbursement_provider_org_provider_activity_id,
                        planned_disbursement.provider_organisation.provider_activity_ref
                    )
                    self.add_to_list(
                        planned_disbursement_provider_org_type,
                        planned_disbursement.provider_organisation.type_id
                    )
                    self.add_to_list(
                        planned_disbursement_provider_org_ref,
                        planned_disbursement.provider_organisation.ref
                    )

                    for narrative in planned_disbursement.provider_organisation.narratives.all():
                        planned_disbursement_provider_org_narrative.append(narrative.content)
                        planned_disbursement_provider_org_narrative_text.append(narrative.content)
                        if narrative.language:
                            planned_disbursement_provider_org_narrative_lang.append(narrative.language.code)

                except PlannedDisbursementProvider.DoesNotExist:
                    pass

                try:

                    self.add_to_list(
                        planned_disbursement_receiver_org_provider_activity_id,
                        planned_disbursement.receiver_organisation.receiver_activity_ref
                    )
                    self.add_to_list(
                        planned_disbursement_receiver_org_type,
                        planned_disbursement.receiver_organisation.type_id
                    )
                    self.add_to_list(
                        planned_disbursement_receiver_org_ref,
                        planned_disbursement.receiver_organisation.ref
                    )

                    for narrative in planned_disbursement.provider_organisation.narratives.all():
                        planned_disbursement_receiver_org_narrative.append(narrative.content)
                        planned_disbursement_receiver_org_narrative_text.append(narrative.content)
                        if narrative.language:
                            planned_disbursement_receiver_org_narrative_lang.append(narrative.language.code)

                except PlannedDisbursementReceiver.DoesNotExist:
                    pass

            self.set_field('planned_disbursement', json.dumps(planned_disbursement_list), representation)
            self.set_field('planned_disbursement_type', planned_disbursement_type, representation)
            self.set_field(
                'planned_disbursement_period_start_iso_date',
                planned_disbursement_period_start_iso_date,
                representation
            )
            self.set_field(
                'planned_disbursement_period_end_iso_date',
                planned_disbursement_period_end_iso_date,
                representation
            )
            self.set_field('planned_disbursement_value_currency', planned_disbursement_value_currency, representation)
            self.set_field('planned_disbursement_value_date', planned_disbursement_value_date, representation)
            self.set_field('planned_disbursement_value', planned_disbursement_value, representation)
            self.set_field(
                'planned_disbursement_provider_org_provider_activity_id',
                planned_disbursement_provider_org_provider_activity_id,
                representation
            )
            self.set_field(
                'planned_disbursement_provider_org_type',
                planned_disbursement_provider_org_type,
                representation
            )
            self.set_field(
                'planned_disbursement_provider_org_ref',
                planned_disbursement_provider_org_ref,
                representation
            )
            self.set_field(
                'planned_disbursement_provider_org_narrative',
                planned_disbursement_provider_org_narrative,
                representation
            )
            self.set_field(
                'planned_disbursement_provider_org_narrative_lang',
                planned_disbursement_provider_org_narrative_lang,
                representation
            )
            self.set_field(
                'planned_disbursement_provider_org_narrative_text',
                planned_disbursement_provider_org_narrative_text,
                representation
            )
            self.set_field(
                'planned_disbursement_receiver_org_provider_activity_id',
                planned_disbursement_receiver_org_provider_activity_id,
                representation
            )
            self.set_field(
                'planned_disbursement_receiver_org_type',
                planned_disbursement_receiver_org_type,
                representation
            )
            self.set_field(
                'planned_disbursement_receiver_org_ref',
                planned_disbursement_receiver_org_ref,
                representation
            )
            self.set_field(
                'planned_disbursement_receiver_org_narrative',
                planned_disbursement_receiver_org_narrative,
                representation
            )
            self.set_field(
                'planned_disbursement_receiver_org_narrative_lang',
                planned_disbursement_receiver_org_narrative_lang,
                representation
            )
            self.set_field(
                'planned_disbursement_receiver_org_narrative_text',
                planned_disbursement_receiver_org_narrative_text,
                representation
            )

    def transaction(self, activity, representation):
        transaction_all = activity.transaction_set.all()
        if transaction_all:
            transaction_list = list()
            transaction_ref = list()
            transaction_humanitarian = list()
            transaction_type = list()
            transaction_date_iso_date = list()
            transaction_value_currency = list()
            transaction_value_date = list()
            transaction_value = list()

            transaction_provider_org_provider_activity_id = list()
            transaction_provider_org_type = list()
            transaction_provider_org_ref = list()

            transaction_provider_org_narrative = list()
            transaction_provider_org_narrative_lang = list()
            transaction_provider_org_narrative_text = list()

            transaction_receiver_org_receiver_activity_id = list()
            transaction_receiver_org_type = list()
            transaction_receiver_org_ref = list()

            transaction_receiver_org_narrative = list()
            transaction_receiver_org_narrative_lang = list()
            transaction_receiver_org_narrative_text = list()

            transaction_disburstment_channel_code = list()

            transaction_sector_vocabulary = list()
            transaction_sector_vocabulary_uri = list()
            transaction_sector_code = list()

            transaction_recipient_country_code = list()
            transaction_recipient_region_code = list()
            transaction_recipient_region_vocabulary = list()
            transaction_flow_type_code = list()
            transaction_finance_type_code = list()

            transaction_aid_type_code = list()
            transaction_aid_type_vocabulary = list()
            transaction_tied_status_code = list()

            for transaction in transaction_all:
                self.add_to_list(transaction_ref, transaction.ref)
                self.add_to_list(
                    transaction_humanitarian,
                    '1' if transaction.humanitarian else '0'
                )
                self.add_to_list(transaction_type, transaction.transaction_type_id)
                self.add_to_list(
                    transaction_date_iso_date,
                    str(transaction.transaction_date.strftime(
                        "%Y-%m-%d")) if transaction.transaction_date else None
                )
                self.add_to_list(transaction_value_currency, transaction.currency_id)
                self.add_to_list(
                    transaction_value_date,
                    str(transaction.value_date.strftime(
                        "%Y-%m-%d")) if transaction.value_date else None
                )
                self.add_to_list(
                    transaction_value,
                    str(transaction.value) if transaction.value > 0 else None
                )

                transaction_list.append(TransactionSerializer(transaction).data)

                try:
                    self.add_to_list(
                        transaction_provider_org_provider_activity_id,
                        transaction.provider_organisation.provider_activity_ref
                    )
                    self.add_to_list(
                        transaction_provider_org_type,
                        transaction.provider_organisation.type_id
                    )
                    self.add_to_list(
                        transaction_provider_org_ref,
                        transaction.provider_organisation.ref
                    )

                    for narrative in transaction.provider_organisation.narratives.all():
                        transaction_provider_org_narrative.append(narrative.content)
                        transaction_provider_org_narrative_text.append(narrative.content)
                        if narrative.language:
                            transaction_provider_org_narrative_lang.append(narrative.language.code)

                except TransactionProvider.DoesNotExist:
                    pass

                try:
                    self.add_to_list(
                        transaction_receiver_org_receiver_activity_id,
                        transaction.receiver_organisation.receiver_activity_ref
                    )
                    self.add_to_list(
                        transaction_receiver_org_type,
                        transaction.receiver_organisation.type_id
                    )
                    self.add_to_list(
                        transaction_receiver_org_ref,
                        transaction.receiver_organisation.ref
                    )

                    for narrative in transaction.receiver_organisation.narratives.all():
                        transaction_receiver_org_narrative.append(narrative.content)
                        transaction_receiver_org_narrative_text.append(narrative.content)
                        if narrative.language:
                            transaction_receiver_org_narrative_lang.append(narrative.language.code)

                except TransactionReceiver.DoesNotExist:
                    pass

                self.add_to_list(
                    transaction_disburstment_channel_code,
                    transaction.disbursement_channel_id
                )

                for transaction_sector in transaction.transactionsector_set.all():
                    self.add_to_list(
                        transaction_sector_vocabulary,
                        transaction_sector.vocabulary_id
                    )
                    self.add_to_list(
                        transaction_sector_vocabulary_uri,
                        transaction_sector.vocabulary_uri
                    )
                    self.add_to_list(
                        transaction_sector_code,
                        transaction_sector.sector_id
                    )

                for transaction_recipient_country in transaction.transactionrecipientcountry_set.all():
                    self.add_to_list(
                        transaction_recipient_country_code,
                        transaction_recipient_country.country_id
                    )

                for transaction_recipient_region in transaction.transactionrecipientregion_set.all():
                    self.add_to_list(
                        transaction_recipient_region_code,
                        transaction_recipient_region.region_id
                    )
                    self.add_to_list(
                        transaction_recipient_region_vocabulary,
                        transaction_recipient_region.vocabulary_id
                    )

                self.add_to_list(
                    transaction_flow_type_code,
                    transaction.flow_type_id
                )
                self.add_to_list(
                    transaction_finance_type_code,
                    transaction.finance_type_id
                )

                for transaction_aid_type in transaction.transactionaidtype_set.all():
                    self.add_to_list(
                        transaction_aid_type_code,
                        transaction_aid_type.aid_type.code
                    )
                    self.add_to_list(
                        transaction_aid_type_vocabulary,
                        transaction_aid_type.aid_type.vocabulary_id
                    )

                self.add_to_list(
                    transaction_tied_status_code,
                    transaction.tied_status_id
                )

            self.set_field(
                'transaction',
                json.dumps(transaction_list),
                representation
            )
            self.set_field(
                'transaction_ref',
                transaction_ref,
                representation
            )
            self.set_field(
                'transaction_humanitarian',
                transaction_humanitarian,
                representation
            )
            self.set_field(
                'transaction_type',
                transaction_type,
                representation
            )
            self.set_field(
                'transaction_date_iso_date',
                transaction_date_iso_date,
                representation
            )
            self.set_field(
                'transaction_value_currency',
                transaction_value_currency,
                representation
            )
            self.set_field(
                'transaction_value_date',
                transaction_value_date,
                representation
            )
            self.set_field(
                'transaction_value',
                transaction_value,
                representation
            )
            self.set_field(
                'transaction_provider_org_provider_activity_id',
                transaction_provider_org_provider_activity_id,
                representation
            )
            self.set_field(
                'transaction_provider_org_type',
                transaction_provider_org_type,
                representation
            )
            self.set_field(
                'transaction_provider_org_ref',
                transaction_provider_org_ref,
                representation
            )
            self.set_field(
                'transaction_provider_org_narrative',
                transaction_provider_org_narrative,
                representation
            )
            self.set_field(
                'transaction_provider_org_narrative_lang',
                transaction_provider_org_narrative_lang,
                representation
            )
            self.set_field(
                'transaction_provider_org_narrative_text',
                transaction_provider_org_narrative_text ,
                representation
            )
            self.set_field(
                'transaction_receiver_org_receiver_activity_id',
                transaction_receiver_org_receiver_activity_id,
                representation
            )
            self.set_field(
                'transaction_receiver_org_type',
                transaction_receiver_org_type,
                representation
            )
            self.set_field(
                'transaction_receiver_org_ref',
                transaction_receiver_org_ref,
                representation
            )
            self.set_field(
                'transaction_receiver_org_narrative',
                transaction_receiver_org_narrative,
                representation
            )
            self.set_field(
                'transaction_receiver_org_narrative_lang',
                transaction_receiver_org_narrative_lang,
                representation
            )
            self.set_field(
                'transaction_receiver_org_narrative_text',
                transaction_receiver_org_narrative_text,
                representation
            )
            self.set_field(
                'transaction_disburstment_channel_code',
                transaction_disburstment_channel_code,
                representation
            )
            self.set_field(
                'transaction_sector_vocabulary',
                transaction_sector_vocabulary,
                representation
            )
            self.set_field(
                'transaction_sector_vocabulary_uri',
                transaction_sector_vocabulary_uri,
                representation
            )
            self.set_field(
                'transaction_sector_code',
                transaction_sector_code,
                representation
            )
            self.set_field(
                'transaction_recipient_country_code',
                transaction_recipient_country_code,
                representation
            )
            self.set_field(
                'transaction_recipient_region_code',
                transaction_recipient_region_code,
                representation
            )
            self.set_field(
                'transaction_recipient_region_vocabulary',
                transaction_recipient_region_vocabulary,
                representation
            )
            self.set_field(
                'transaction_flow_type_code',
                transaction_flow_type_code,
                representation
            )
            self.set_field(
                'transaction_aid_type_code',
                transaction_aid_type_code,
                representation
            )
            self.set_field(
                'transaction_aid_type_vocabulary',
                transaction_aid_type_vocabulary,
                representation
            )
            self.set_field(
                'transaction_tied_status_code',
                transaction_tied_status_code,
                representation
            )

    def document_link(self, activity, representation):
        document_link_all = activity.documentlink_set.filter(
            result_id__isnull=True,
            result_indicator_id__isnull=True,
            result_indicator_baseline_id__isnull=True,
            result_indicator_period_actual_id__isnull=True,
            result_indicator_period_target_id__isnull=True
        )
        if document_link_all:
            document_link_list = list()
            document_link_format = list()
            document_link_url = list()

            document_link_title_narrative = list()
            document_link_title_narrative_lang = list()
            document_link_title_narrative_text = list()

            document_link_description_narrative = list()
            document_link_description_narrative_lang = list()
            document_link_description_narrative_text = list()

            document_link_category_code = list()
            document_link_language_code = list()
            document_link_document_date_iso_date = list()

            for document_link in document_link_all:
                self.add_to_list(
                    document_link_format,
                    document_link.file_format_id
                )
                self.add_to_list(
                    document_link_url,
                    document_link.url
                )
                self.add_to_list(
                    document_link_document_date_iso_date,
                    str(document_link.iso_date.strftime(
                        "%Y-%m-%d")) if document_link.iso_date else None
                )

                document_link_list.append(DocumentLinkSerializer(document_link).data)

                for narrative in document_link.documentlinktitle.narratives.all():
                    document_link_title_narrative.append(narrative.content)
                    document_link_title_narrative_text.append(narrative.content)
                    if narrative.language:
                        document_link_title_narrative_lang.append(narrative.language.code)

                for narrative in document_link.documentlinkdescription.narratives.all():
                    document_link_description_narrative.append(narrative.content)
                    document_link_description_narrative_text.append(narrative.content)
                    if narrative.language:
                        document_link_description_narrative_lang.append(narrative.language.code)

                for document_link_category in document_link.documentlinkcategory_set.all():
                    self.add_to_list(
                        document_link_category_code,
                        document_link_category.category_id
                    )

                for document_link_language in document_link.documentlinklanguage_set.all():
                    self.add_to_list(
                        document_link_language_code,
                        document_link_language.language_id
                    )

            self.set_field(
                'document_link',
                json.dumps(document_link_list),
                representation
            )
            self.set_field(
                'document_link_format',
                document_link_format,
                representation
            )
            self.set_field(
                'document_link_url',
                document_link_url,
                representation
            )
            self.set_field(
                'document_link_title_narrative',
                document_link_title_narrative,
                representation
            )
            self.set_field(
                'document_link_title_narrative_lang',
                document_link_title_narrative_lang,
                representation
            )
            self.set_field(
                'document_link_title_narrative_text',
                document_link_title_narrative_text,
                representation
            )
            self.set_field(
                'document_link_description_narrative',
                document_link_description_narrative,
                representation
            )
            self.set_field(
                'document_link_description_narrative_lang',
                document_link_description_narrative_lang,
                representation
            )
            self.set_field(
                'document_link_description_narrative_text',
                document_link_description_narrative_text,
                representation
            )
            self.set_field(
                'document_link_category_code',
                document_link_category_code,
                representation
            )
            self.set_field(
                'document_link_language_code',
                document_link_language_code,
                representation
            )
            self.set_field(
                'document_link_document_date_iso_date',
                document_link_document_date_iso_date,
                representation
            )

    def conditions(self, activity, representation):
        try:
            conditions = ConditionsSerializer(activity.conditions).data
            conditions_attached = '1' if activity.conditions.attached else '0'
            conditions_condition_type = list()
            conditions_condition_narrative = list()
            conditions_condition_narrative_lang = list()
            conditions_condition_narrative_text = list()
            for condition in activity.conditions.condition_set.all():
                self.add_to_list(
                    conditions_condition_type,
                    condition.type_id
                )

                for narrative in condition.narratives.all():
                    conditions_condition_narrative.append(narrative.content)
                    conditions_condition_narrative_text.append(narrative.content)
                    if narrative.language:
                        conditions_condition_narrative_lang.append(narrative.language.code)

            self.set_field(
                'conditions',
                json.dumps(conditions),
                representation
            )
            self.set_field(
                'conditions_attached',
                conditions_attached,
                representation
            )
            self.set_field(
                'conditions_condition_type',
                conditions_condition_type,
                representation
            )
            self.set_field(
                'conditions_condition_narrative',
                conditions_condition_narrative,
                representation
            )
            self.set_field(
                'conditions_condition_narrative_lang',
                conditions_condition_narrative_lang,
                representation
            )
            self.set_field(
                'conditions_condition_narrative_text',
                conditions_condition_narrative_text,
                representation
            )
        except Conditions.DoesNotExist:
            pass

    def result(self, activity, representation):
        result_all = activity.result_set.all()
        if result_all:
            result_list = list()
            result_type = list()
            result_aggregation_status = list()

            result_title_narrative = list()
            result_title_narrative_lang = list()
            result_title_narrative_text = list()

            result_description_narrative = list()
            result_description_narrative_lang = list()
            result_description_narrative_text = list()

            result_document_link = list()
            result_document_link_url = list()
            result_document_link_format = list()

            result_document_link_title_narrative = list()
            result_document_link_title_narrative_lang = list()
            result_document_link_title_narrative_text = list()

            result_document_link_description_narrative = list()
            result_document_link_description_narrative_lang = list()
            result_document_link_description_narrative_text = list()

            result_document_link_category_code = list()
            result_document_link_language_code = list()
            result_document_link_document_date_iso_date = list()

            # result_reference = list()
            result_reference_code = list()
            result_reference_vocabulary = list()
            result_reference_vocabulary_uri = list()

            # result_indicator = list()
            result_indicator_measure = list()
            result_indicator_ascending = list()
            result_indicator_aggregation_status = list()

            result_indicator_title_narrative = list()
            result_indicator_title_narrative_lang = list()
            result_indicator_title_narrative_text = list()

            result_indicator_description_narrative = list()
            result_indicator_description_narrative_lang = list()
            result_indicator_description_narrative_text = list()

            result_indicator_document_link_url = list()
            result_indicator_document_link_format = list()

            result_indicator_document_link_title_narrative = list()
            result_indicator_document_link_title_narrative_lang = list()
            result_indicator_document_link_title_narrative_text = list()

            result_indicator_document_link_description_narrative = list()
            result_indicator_document_link_description_narrative_lang = list()
            result_indicator_document_link_description_narrative_text = list()

            result_indicator_document_link_category_code = list()
            result_indicator_document_link_language_code = list()
            result_indicator_document_link_document_date_iso_date = list()

            # result_indicator_reference = list()
            result_indicator_reference_code = list()
            result_indicator_reference_vocabulary = list()
            result_indicator_reference_vocabulary_uri = list()

            result_indicator_baseline_year = list()
            result_indicator_baseline_iso_date = list()
            result_indicator_baseline_value = list()
            result_indicator_baseline_location_ref = list()
            result_indicator_baseline_dimension_name = list()
            result_indicator_baseline_dimension_value = list()

            result_indicator_baseline_comment_narrative = list()
            result_indicator_baseline_comment_narrative_lang = list()
            result_indicator_baseline_comment_narrative_text = list()

            result_indicator_baseline_document_link_url = list()
            result_indicator_baseline_document_link_format = list()

            result_indicator_baseline_document_link_title = list()
            result_indicator_baseline_document_link_title_narrative_lang = list()
            result_indicator_baseline_document_link_title_narrative_text = list()

            result_indicator_baseline_document_link_description = list()
            result_indicator_baseline_document_link_description_lang = list()
            result_indicator_baseline_document_link_description_text = list()

            result_indicator_baseline_document_link_category_code = list()
            result_indicator_baseline_document_link_language_code = list()
            result_indicator_baseline_document_link_document_date_iso_date = list()

            result_indicator_period_period_start_iso_date = list()
            result_indicator_period_period_end_iso_date = list()

            result_indicator_period_target_value = list()
            result_indicator_period_target_location_ref = list()

            result_indicator_period_target_dimension_name = list()
            result_indicator_period_target_dimension_value = list()

            result_indicator_period_target_comment_narrative = list()
            result_indicator_period_target_comment_narrative_lang = list()
            result_indicator_period_target_comment_narrative_text = list()

            result_indicator_period_target_document_link_url = list()
            result_indicator_period_target_document_link_format = list()

            result_indicator_period_target_document_link_title_narrative = list()
            result_indicator_period_target_document_link_title_narrative_lang = list()
            result_indicator_period_target_document_link_title_narrative_text = list()

            result_indicator_period_target_document_link_description_narrative = list()
            result_indicator_period_target_document_link_description_narrative_lang = list()
            result_indicator_period_target_document_link_description_narrative_text = list()

            result_indicator_period_target_document_link_category_code = list()
            result_indicator_period_target_document_link_language_code = list()
            result_indicator_period_target_document_link_document_date_iso_date = list()

            result_indicator_period_actual_value = list()
            result_indicator_period_actual_location_ref = list()

            result_indicator_period_actual_dimension_name = list()
            result_indicator_period_actual_dimension_value = list()

            result_indicator_period_actual_comment_narrative = list()
            result_indicator_period_actual_comment_narrative_lang = list()
            result_indicator_period_actual_comment_narrative_text = list()

            result_indicator_period_actual_document_link_url = list()
            result_indicator_period_actual_document_link_format = list()

            result_indicator_period_actual_document_link_title_narrative = list()
            result_indicator_period_actual_document_link_title_narrative_lang = list()
            result_indicator_period_actual_document_link_title_narrative_text = list()

            result_indicator_period_actual_document_link_description_narrative = list()
            result_indicator_period_actual_document_link_description_narrative_lang = list()
            result_indicator_period_actual_document_link_description_narrative_text = list()

            result_indicator_period_actual_document_link_category_code = list()
            result_indicator_period_actual_document_link_language_code = list()
            result_indicator_period_actual_document_link_document_date_iso_date = list()

            for result in result_all:
                result_list.append(ResultSerializer(result).data)

                self.add_to_list(
                    result_type,
                    result.type_id
                )
                self.add_to_list(
                    result_aggregation_status,
                    '1' if result.aggregation_status else '0'
                )

                try:
                    for narrative in result.resulttitle.narratives.all():
                        result_title_narrative.append(narrative.content)
                        result_title_narrative_text.append(narrative.content)
                        if narrative.language:
                            result_title_narrative_lang.append(narrative.language.code)
                except ResultTitle.DoesNotExist:
                    pass

                try:
                    for narrative in result.resultdescription.narratives.all():
                        result_description_narrative.append(narrative.content)
                        result_description_narrative_text.append(narrative.content)
                        if narrative.language:
                            result_description_narrative_lang.append(narrative.language.code)
                except ResultDescription.DoesNotExist:
                    pass

                for document_link in result.documentlink_set.all():
                    self.add_to_list(
                        result_document_link_url,
                        document_link.url
                    )
                    self.add_to_list(
                        result_document_link_format,
                        document_link.file_format_id
                    )

                    try:
                        for narrative in document_link.documentlinktitle.narratives.all():
                            result_document_link_title_narrative.append(narrative.content)
                            result_document_link_title_narrative_text.append(narrative.content)
                            if narrative.language:
                                result_document_link_title_narrative_lang.append(narrative.language.code)
                    except DocumentLinkTitle.DoesNotExist:
                        pass

                    try:
                        for narrative in document_link.documentlinkdescription.narratives.all():
                            result_document_link_description_narrative.append(narrative.content)
                            result_document_link_description_narrative_text.append(narrative.content)
                            if narrative.language:
                                result_document_link_description_narrative_lang.append(narrative.language.code)
                    except DocumentLinkDescription.DoesNotExist:
                        pass

                    for document_link_category in document_link.documentlinkcategory_set.all():
                        self.add_to_list(
                            result_document_link_category_code,
                            document_link_category.category_id
                        )

                    for document_link_language in document_link.documentlinklanguage_set.all():
                        self.add_to_list(
                            result_document_link_language_code,
                            document_link_language.language_id
                        )

                    self.add_to_list(
                        result_document_link_document_date_iso_date,
                        str(document_link.iso_date.strftime(
                            "%Y-%m-%d")) if document_link.iso_date else None
                    )

                for result_reference in result.resultreference_set.all():
                    self.add_to_list(
                        result_reference_code,
                        result_reference.code
                    )
                    self.add_to_list(
                        result_reference_vocabulary,
                        result_reference.vocabulary_id
                    )
                    self.add_to_list(
                        result_reference_vocabulary_uri,
                        result_reference.vocabulary_uri
                    )

                for result_indicator in result.resultindicator_set.all():
                    self.add_to_list(
                        result_indicator_measure,
                        result_indicator.measure_id
                    )
                    self.add_to_list(
                        result_indicator_ascending,
                        '1' if result_indicator.ascending else '0'
                    )
                    self.add_to_list(
                        result_indicator_aggregation_status,
                        '1' if result_indicator.aggregation_status else '0'
                    )

                    try:
                        for narrative in result_indicator.resultindicatortitle.narratives.all():
                            result_indicator_title_narrative.append(narrative.content)
                            result_indicator_title_narrative_text.append(narrative.content)
                            if narrative.language:
                                result_indicator_title_narrative_lang.append(narrative.language.code)
                    except ResultIndicatorTitle.DoesNotExist:
                        pass

                    try:
                        for narrative in result_indicator.resultindicatordescription.narratives.all():
                            result_indicator_description_narrative.append(narrative.content)
                            result_indicator_description_narrative_text.append(narrative.content)
                            if narrative.language:
                                result_indicator_description_narrative_lang.append(narrative.language.code)
                    except ResultIndicatorTitle.DoesNotExist:
                        pass

                    for result_indicator_document_link in result_indicator.result_indicator_document_links.all():
                        self.add_to_list(
                            result_indicator_document_link_url,
                            result_indicator_document_link.url
                        )
                        self.add_to_list(
                            result_indicator_document_link_format,
                            result_indicator_document_link.file_format_id
                        )

                        try:
                            for narrative in result_indicator_document_link.documentlinktitle.narratives.all():
                                result_indicator_document_link_title_narrative.append(narrative.content)
                                result_indicator_document_link_title_narrative_text.append(narrative.content)
                                if narrative.language:
                                    result_indicator_document_link_title_narrative_lang.append(narrative.language.code)
                        except ResultIndicatorTitle.DoesNotExist:
                            pass

                        try:
                            for narrative in result_indicator_document_link.documentlinkdescription.narratives.all():
                                result_indicator_document_link_description_narrative.append(narrative.content)
                                result_indicator_document_link_description_narrative_text.append(narrative.content)
                                if narrative.language:
                                    result_indicator_document_link_description_narrative_lang.append(narrative.language.code)  # NOQA: E501
                        except ResultIndicatorTitle.DoesNotExist:
                            pass

                        for document_link_category in result_indicator_document_link.documentlinkcategory_set.all():
                            self.add_to_list(
                                result_indicator_document_link_category_code,
                                document_link_category.category_id
                            )

                        for document_link_language in result_indicator_document_link.documentlinklanguage_set.all():
                            self.add_to_list(
                                result_indicator_document_link_language_code,
                                document_link_language.language_id
                            )

                        self.add_to_list(
                            result_indicator_document_link_document_date_iso_date,
                            str(result_indicator_document_link.iso_date.strftime(
                                "%Y-%m-%d")) if result_indicator_document_link.iso_date else None
                        )

                    for result_indicator_reference in result_indicator.resultindicatorreference_set.all():
                        self.add_to_list(
                            result_indicator_reference_code,
                            result_indicator_reference.code
                        )
                        self.add_to_list(
                            result_indicator_reference_vocabulary,
                            result_indicator_reference.vocabulary_id
                        )
                        self.add_to_list(
                            result_indicator_reference_vocabulary_uri,
                            result_indicator_reference.indicator_uri
                        )

                    for result_indicator_baseline in result_indicator.resultindicatorbaseline_set.all():
                        self.add_to_list(
                            result_indicator_baseline_year,
                            result_indicator_baseline.year
                        )
                        self.add_to_list(
                            result_indicator_baseline_iso_date,
                            str(result_indicator_baseline.iso_date.strftime(
                                "%Y-%m-%d")) if result_indicator_baseline.iso_date else None
                        )
                        self.add_to_list(
                            result_indicator_baseline_value,
                            result_indicator_baseline.value
                        )

                        for result_indicator_baseline_location in result_indicator_baseline.location_set.all():
                            self.add_to_list(
                                result_indicator_baseline_location_ref,
                                result_indicator_baseline_location.ref
                            )

                        for result_indicator_baseline_dimension in result_indicator_baseline.resultindicatorbaselinedimension_set.all():  # NOQA: E501
                            self.add_to_list(
                                result_indicator_baseline_dimension_name,
                                result_indicator_baseline_dimension.name
                            )
                            self.add_to_list(
                                result_indicator_baseline_dimension_value,
                                result_indicator_baseline_dimension.value
                            )

                        try:
                            for narrative in result_indicator_baseline.resultindicatorbaselinecomment.narratives.all():
                                result_indicator_baseline_comment_narrative.append(narrative.content)
                                result_indicator_baseline_comment_narrative_text.append(narrative.content)
                                if narrative.language:
                                    result_indicator_baseline_comment_narrative_lang.append(narrative.language.code)  # NOQA: E501
                        except ResultIndicatorBaselineComment.DoesNotExist:
                            pass

                        for result_indicator_baseline_document_link in result_indicator_baseline.baseline_document_links.all(): # NOQA: E501
                            self.add_to_list(
                                result_indicator_baseline_document_link_url,
                                result_indicator_baseline_document_link.url
                            )
                            self.add_to_list(
                                result_indicator_baseline_document_link_format,
                                result_indicator_baseline_document_link.file_format_id
                            )

                            try:
                                for narrative in result_indicator_baseline_document_link.documentlinktitle.narratives.all():
                                    result_indicator_baseline_document_link_title.append(narrative.content)
                                    result_indicator_baseline_document_link_title_narrative_text.append(narrative.content)
                                    if narrative.language:
                                        result_indicator_baseline_document_link_title_narrative_lang.append(
                                            narrative.language.code)
                            except ResultIndicatorTitle.DoesNotExist:
                                pass

                            try:
                                for narrative in result_indicator_baseline_document_link.documentlinkdescription.narratives.all():
                                    result_indicator_baseline_document_link_description.append(narrative.content)
                                    result_indicator_baseline_document_link_description_text.append(narrative.content)
                                    if narrative.language:
                                        result_indicator_baseline_document_link_description_lang.append(
                                            narrative.language.code)  # NOQA: E501
                            except DocumentLinkTitle.DoesNotExist:
                                pass

                            for document_link_category in result_indicator_baseline_document_link.documentlinkcategory_set.all():
                                self.add_to_list(
                                    result_indicator_baseline_document_link_category_code,
                                    document_link_category.category_id
                                )

                            for document_link_language in result_indicator_baseline_document_link.documentlinklanguage_set.all():
                                self.add_to_list(
                                    result_indicator_baseline_document_link_language_code,
                                    document_link_language.language_id
                                )

                            self.add_to_list(
                                result_indicator_baseline_document_link_document_date_iso_date,
                                str(result_indicator_baseline_document_link.iso_date.strftime(
                                    "%Y-%m-%d")) if result_indicator_baseline_document_link.iso_date else None
                            )

                    for result_period in result_indicator.resultindicatorperiod_set.all():
                        self.add_to_list(
                            result_indicator_period_period_start_iso_date,
                            str(result_period.period_start.strftime(
                                "%Y-%m-%d")) if result_period.period_start else None
                        )
                        self.add_to_list(
                            result_indicator_period_period_end_iso_date,
                            str(result_period.period_end.strftime(
                                "%Y-%m-%d")) if result_period.period_end else None
                        )

                        for result_period_target in result_period.targets.all():
                            self.add_to_list(
                                result_indicator_period_target_value,
                                result_period_target.value
                            )

                            for result_period_target_location in result_period_target.resultindicatorperiodtargetlocation_set.all():
                                self.add_to_list(
                                    result_indicator_period_target_location_ref,
                                    result_period_target_location.ref
                                )

                            for result_period_target_dimension in result_period_target.resultindicatorperiodtargetdimension_set.all():
                                self.add_to_list(
                                    result_indicator_period_target_dimension_name,
                                    result_period_target_dimension.name
                                )
                                self.add_to_list(
                                    result_indicator_period_target_dimension_value,
                                    result_period_target_dimension.value
                                )

                            for result_period_target_comment in result_period_target.resultindicatorperiodtargetcomment_set.all():
                                for narrative in result_period_target_comment.narratives.all():
                                    result_indicator_period_target_comment_narrative.append(narrative.content)
                                    result_indicator_period_target_comment_narrative_text.append(narrative.content)
                                    if narrative.language:
                                        result_indicator_period_target_comment_narrative_lang.append(
                                            narrative.language.code)

                            for document_link in result_period_target.period_target_document_links.all(): # NOQA: E501
                                self.add_to_list(
                                    result_indicator_period_target_document_link_url,
                                    document_link.url
                                )
                                self.add_to_list(
                                    result_indicator_period_target_document_link_format,
                                    document_link.file_format_id
                                )

                                try:
                                    for narrative in document_link.documentlinktitle.narratives.all():
                                        result_indicator_period_target_document_link_title_narrative.append(narrative.content)
                                        result_indicator_period_target_document_link_title_narrative_text.append(narrative.content)
                                        if narrative.language:
                                            result_indicator_period_target_document_link_title_narrative_lang.append(
                                                narrative.language.code)
                                except DocumentLinkTitle.DoesNotExist:
                                    pass

                                try:
                                    for narrative in document_link.documentlinkdescription.narratives.all():
                                        result_indicator_period_target_document_link_description_narrative.append(narrative.content)
                                        result_indicator_period_target_document_link_description_narrative_text.append(narrative.content)
                                        if narrative.language:
                                            result_indicator_period_target_document_link_description_narrative_lang.append(
                                                narrative.language.code)  # NOQA: E501
                                except DocumentLinkTitle.DoesNotExist:
                                    pass

                                for document_link_category in document_link.documentlinkcategory_set.all():
                                    self.add_to_list(
                                        result_indicator_period_target_document_link_category_code,
                                        document_link_category.category_id
                                    )

                                for document_link_language in document_link.documentlinklanguage_set.all():
                                    self.add_to_list(
                                        result_indicator_period_target_document_link_language_code,
                                        document_link_language.language_id
                                    )

                                self.add_to_list(
                                    result_indicator_period_target_document_link_document_date_iso_date,
                                    str(document_link.iso_date.strftime(
                                        "%Y-%m-%d")) if document_link.iso_date else None
                                )

                        for result_period_actual in result_period.actuals.all():
                            self.add_to_list(
                                result_indicator_period_actual_value,
                                result_period_actual.value
                            )

                            for result_period_actual_location in result_period_actual.resultindicatorperiodactuallocation_set.all():
                                self.add_to_list(
                                    result_indicator_period_actual_location_ref,
                                    result_period_actual_location.ref
                                )

                            for result_period_actual_dimension in result_period_actual.resultindicatorperiodactualdimension_set.all():
                                self.add_to_list(
                                    result_indicator_period_actual_dimension_name,
                                    result_period_actual_dimension.name
                                )
                                self.add_to_list(
                                    result_indicator_period_actual_dimension_value,
                                    result_period_actual_dimension.value
                                )

                            for result_period_actual_comment in result_period_actual.resultindicatorperiodactualcomment_set.all():
                                for narrative in result_period_actual_comment.narratives.all():
                                    result_indicator_period_actual_comment_narrative.append(narrative.content)
                                    result_indicator_period_actual_comment_narrative_text.append(narrative.content)
                                    if narrative.language:
                                        result_indicator_period_actual_comment_narrative_lang.append(
                                            narrative.language.code)

                            for document_link in result_period_actual.period_actual_document_links.all(): # NOQA: E501
                                self.add_to_list(
                                    result_indicator_period_actual_document_link_url,
                                    document_link.url
                                )
                                self.add_to_list(
                                    result_indicator_period_actual_document_link_format,
                                    document_link.file_format_id
                                )

                                try:
                                    for narrative in document_link.documentlinktitle.narratives.all():
                                        result_indicator_period_actual_document_link_title_narrative.append(narrative.content)
                                        result_indicator_period_actual_document_link_title_narrative_text.append(narrative.content)
                                        if narrative.language:
                                            result_indicator_period_actual_document_link_title_narrative_lang.append(
                                                narrative.language.code)
                                except DocumentLinkTitle.DoesNotExist:
                                    pass

                                try:
                                    for narrative in document_link.documentlinkdescription.narratives.all():
                                        result_indicator_period_actual_document_link_description_narrative.append(narrative.content)
                                        result_indicator_period_actual_document_link_description_narrative_text.append(narrative.content)
                                        if narrative.language:
                                            result_indicator_period_actual_document_link_description_narrative_lang.append(
                                                narrative.language.code)  # NOQA: E501
                                except DocumentLinkTitle.DoesNotExist:
                                    pass

                                for document_link_category in document_link.documentlinkcategory_set.all():
                                    self.add_to_list(
                                        result_indicator_period_actual_document_link_category_code,
                                        document_link_category.category_id
                                    )

                                for document_link_language in document_link.documentlinklanguage_set.all():
                                    self.add_to_list(
                                        result_indicator_period_actual_document_link_language_code,
                                        document_link_language.language_id
                                    )

                                self.add_to_list(
                                    result_indicator_period_actual_document_link_document_date_iso_date,
                                    str(document_link.iso_date.strftime(
                                        "%Y-%m-%d")) if document_link.iso_date else None
                                )

            self.set_field(
                'result',
                json.dumps(result_list),
                representation
            )
            self.set_field(
                'result_type',
                result_type,
                representation
            )
            self.set_field(
                'result_aggregation_status',
                result_aggregation_status,
                representation
            )
            self.set_field(
                'result_title_narrative',
                result_title_narrative,
                representation
            )
            self.set_field(
                'result_title_narrative_lang',
                result_title_narrative_lang,
                representation
            )
            self.set_field(
                'result_title_narrative_text',
                result_title_narrative_text,
                representation
            )
            self.set_field(
                'result_description_narrative',
                result_description_narrative,
                representation
            )
            self.set_field(
                'result_description_narrative_lang',
                result_description_narrative_lang,
                representation
            )
            self.set_field(
                'result_description_narrative_text',
                result_description_narrative_text,
                representation
            )
            self.set_field(
                'result_document_link_url',
                result_document_link_url,
                representation
            )
            self.set_field(
                'result_document_link_format',
                result_document_link_format,
                representation
            )
            self.set_field(
                'result_document_link_title_narrative',
                result_document_link_title_narrative,
                representation
            )
            self.set_field(
                'result_document_link_title_narrative_lang',
                result_document_link_title_narrative_lang,
                representation
            )
            self.set_field(
                'result_document_link_title_narrative_text',
                result_document_link_title_narrative_text,
                representation
            )
            self.set_field(
                'result_document_link_description_narrative',
                result_document_link_description_narrative,
                representation
            )
            self.set_field(
                'result_document_link_description_narrative_lang',
                result_document_link_description_narrative_lang,
                representation
            )
            self.set_field(
                'result_document_link_description_narrative_text',
                result_document_link_description_narrative_text,
                representation
            )
            self.set_field(
                'result_document_link_category_code',
                result_document_link_category_code,
                representation
            )
            self.set_field(
                'result_document_link_language_code',
                result_document_link_language_code,
                representation
            )
            self.set_field(
                'result_document_link_document_date_iso_date',
                result_document_link_document_date_iso_date,
                representation
            )
            self.set_field(
                'result_reference_code',
                result_reference_code,
                representation
            )
            self.set_field(
                'result_indicator_measure',
                result_indicator_measure,
                representation
            )
            self.set_field(
                'result_indicator_ascending',
                result_indicator_ascending,
                representation
            )
            self.set_field(
                'result_indicator_aggregation_status',
                result_indicator_aggregation_status,
                representation
            )
            self.set_field(
                'result_indicator_title_narrative',
                result_indicator_title_narrative,
                representation
            )
            self.set_field(
                'result_indicator_title_narrative_lang',
                result_indicator_title_narrative_lang,
                representation
            )
            self.set_field(
                'result_indicator_title_narrative_text',
                result_indicator_title_narrative_text,
                representation
            )
            self.set_field(
                'result_indicator_description_narrative',
                result_indicator_description_narrative,
                representation
            )
            self.set_field(
                'result_indicator_description_narrative_lang',
                result_indicator_description_narrative_lang,
                representation
            )
            self.set_field(
                'result_indicator_description_narrative_text',
                result_indicator_description_narrative_text,
                representation
            )
            self.set_field(
                'result_indicator_document_link_url',
                result_indicator_document_link_url,
                representation
            )
            self.set_field(
                'result_indicator_document_link_format',
                result_indicator_document_link_format,
                representation
            )
            self.set_field(
                'result_indicator_document_link_title_narrative',
                result_indicator_document_link_title_narrative,
                representation
            )
            self.set_field(
                'result_indicator_document_link_title_narrative_lang',
                result_indicator_document_link_title_narrative_lang,
                representation
            )
            self.set_field(
                'result_indicator_document_link_title_narrative_text',
                result_indicator_document_link_title_narrative_text,
                representation
            )
            self.set_field(
                'result_indicator_document_link_description_narrative',
                result_indicator_document_link_description_narrative,
                representation
            )
            self.set_field(
                'result_indicator_document_link_description_narrative_lang',
                result_indicator_document_link_description_narrative_lang,
                representation
            )
            self.set_field(
                'result_indicator_document_link_description_narrative_text',
                result_indicator_document_link_description_narrative_text,
                representation
            )
            self.set_field(
                'result_indicator_document_link_category_code',
                result_indicator_document_link_category_code,
                representation
            )
            self.set_field(
                'result_indicator_document_link_language_code',
                result_indicator_document_link_language_code,
                representation
            )
            self.set_field(
                'result_indicator_document_link_document_date_iso_date',
                result_indicator_document_link_document_date_iso_date,
                representation
            )
            self.set_field(
                'result_indicator_reference_code',
                result_indicator_reference_code,
                representation
            )
            self.set_field(
                'result_indicator_reference_vocabulary',
                result_indicator_reference_vocabulary,
                representation
            )
            self.set_field(
                'result_indicator_reference_vocabulary_uri',
                result_indicator_reference_vocabulary_uri,
                representation
            )
            self.set_field(
                'result_indicator_baseline_year',
                result_indicator_baseline_year,
                representation
            )
            self.set_field(
                'result_indicator_baseline_iso_date',
                result_indicator_baseline_iso_date,
                representation
            )
            self.set_field(
                'result_indicator_baseline_value',
                result_indicator_baseline_value,
                representation
            )
            self.set_field(
                'result_indicator_baseline_location_ref',
                result_indicator_baseline_location_ref,
                representation
            )
            self.set_field(
                'result_indicator_baseline_dimension_name',
                result_indicator_baseline_dimension_name,
                representation
            )
            self.set_field(
                'result_indicator_baseline_dimension_value',
                result_indicator_baseline_dimension_value,
                representation
            )
            self.set_field(
                'result_indicator_baseline_comment_narrative',
                result_indicator_baseline_comment_narrative,
                representation
            )
            self.set_field(
                'result_indicator_baseline_comment_narrative_lang',
                result_indicator_baseline_comment_narrative_lang,
                representation
            )
            self.set_field(
                'result_indicator_baseline_comment_narrative_text',
                result_indicator_baseline_comment_narrative_text,
                representation
            )
            self.set_field(
                'result_indicator_baseline_document_link_url',
                result_indicator_baseline_document_link_url,
                representation
            )
            self.set_field(
                'result_indicator_baseline_document_link_format',
                result_indicator_baseline_document_link_format,
                representation
            )
            self.set_field(
                'result_indicator_baseline_document_link_title',
                result_indicator_baseline_document_link_title,
                representation
            )
            self.set_field(
                'result_indicator_baseline_document_link_title_narrative_lang',
                result_indicator_baseline_document_link_title_narrative_lang,
                representation
            )
            self.set_field(
                'result_indicator_baseline_document_link_title_narrative_text',
                result_indicator_baseline_document_link_title_narrative_text,
                representation
            )
            self.set_field(
                'result_indicator_baseline_document_link_description',
                result_indicator_baseline_document_link_description,
                representation
            )
            self.set_field(
                'result_indicator_baseline_document_link_description_lang',
                result_indicator_baseline_document_link_description_lang,
                representation
            )
            self.set_field(
                'result_indicator_baseline_document_link_description_text',
                result_indicator_baseline_document_link_description_text,
                representation
            )
            self.set_field(
                'result_indicator_baseline_document_link_category_code',
                result_indicator_baseline_document_link_category_code,
                representation
            )
            self.set_field(
                'result_indicator_baseline_document_link_language_code',
                result_indicator_baseline_document_link_language_code,
                representation
            )
            self.set_field(
                'result_indicator_baseline_document_link_document_date_iso_date',
                result_indicator_baseline_document_link_document_date_iso_date,
                representation
            )
            self.set_field(
                'result_indicator_period_period_start_iso_date',
                result_indicator_period_period_start_iso_date,
                representation
            )
            self.set_field(
                'result_indicator_period_period_end_iso_date',
                result_indicator_period_period_end_iso_date,
                representation
            )
            self.set_field(
                'result_indicator_period_target_value',
                result_indicator_period_target_value,
                representation
            )
            self.set_field(
                'result_indicator_period_target_location_ref',
                result_indicator_period_target_location_ref,
                representation
            )
            self.set_field(
                'result_indicator_period_target_dimension_name',
                result_indicator_period_target_dimension_name,
                representation
            )
            self.set_field(
                'result_indicator_period_target_dimension_value',
                result_indicator_period_target_dimension_value,
                representation
            )
            self.set_field(
                'result_indicator_period_target_comment_narrative',
                result_indicator_period_target_comment_narrative,
                representation
            )
            self.set_field(
                'result_indicator_period_target_comment_narrative_lang',
                result_indicator_period_target_comment_narrative_lang,
                representation
            )
            self.set_field(
                'result_indicator_period_target_comment_narrative_text',
                result_indicator_period_target_comment_narrative_text,
                representation
            )
            self.set_field(
                'result_indicator_period_target_document_link_url',
                result_indicator_period_target_document_link_url,
                representation
            )
            self.set_field(
                'result_indicator_period_target_document_link_format',
                result_indicator_period_target_document_link_format,
                representation
            )
            self.set_field(
                'result_indicator_period_target_document_link_title_narrative',
                result_indicator_period_target_document_link_title_narrative,
                representation
            )
            self.set_field(
                'result_indicator_period_target_document_link_title_narrative_lang',
                result_indicator_period_target_document_link_title_narrative_lang,
                representation
            )
            self.set_field(
                'result_indicator_period_target_document_link_title_narrative_text',
                result_indicator_period_target_document_link_title_narrative_text,
                representation
            )
            self.set_field(
                'result_indicator_period_target_document_link_description_narrative',
                result_indicator_period_target_document_link_description_narrative,
                representation
            )
            self.set_field(
                'result_indicator_period_target_document_link_description_narrative_lang',
                result_indicator_period_target_document_link_description_narrative_lang,
                representation
            )
            self.set_field(
                'result_indicator_period_target_document_link_description_narrative_text',
                result_indicator_period_target_document_link_description_narrative_text,
                representation
            )
            self.set_field(
                'result_indicator_period_target_document_link_category_code',
                result_indicator_period_target_document_link_category_code,
                representation
            )
            self.set_field(
                'result_indicator_period_target_document_link_language_code',
                result_indicator_period_target_document_link_language_code,
                representation
            )
            self.set_field(
                'result_indicator_period_target_document_link_document_date_iso_date',
                result_indicator_period_target_document_link_document_date_iso_date,
                representation
            )
            self.set_field(
                'result_indicator_period_actual_value',
                result_indicator_period_actual_value,
                representation
            )
            self.set_field(
                'result_indicator_period_actual_location_ref',
                result_indicator_period_actual_location_ref,
                representation
            )
            self.set_field(
                'result_indicator_period_actual_dimension_name',
                result_indicator_period_actual_dimension_name,
                representation
            )
            self.set_field(
                'result_indicator_period_actual_dimension_value',
                result_indicator_period_actual_dimension_value,
                representation
            )
            self.set_field(
                'result_indicator_period_actual_comment_narrative',
                result_indicator_period_actual_comment_narrative,
                representation
            )
            self.set_field(
                'result_indicator_period_actual_comment_narrative_lang',
                result_indicator_period_actual_comment_narrative_lang,
                representation
            )
            self.set_field(
                'result_indicator_period_actual_comment_narrative_text',
                result_indicator_period_actual_comment_narrative_text,
                representation
            )
            self.set_field(
                'result_indicator_period_actual_document_link_url',
                result_indicator_period_actual_document_link_url,
                representation
            )
            self.set_field(
                'result_indicator_period_actual_document_link_format',
                result_indicator_period_actual_document_link_format,
                representation
            )
            self.set_field(
                'result_indicator_period_actual_document_link_title_narrative',
                result_indicator_period_actual_document_link_title_narrative,
                representation
            )
            self.set_field(
                'result_indicator_period_actual_document_link_title_narrative_lang',
                result_indicator_period_actual_document_link_title_narrative_lang,
                representation
            )
            self.set_field(
                'result_indicator_period_actual_document_link_title_narrative_text',
                result_indicator_period_actual_document_link_title_narrative_text,
                representation
            )
            self.set_field(
                'result_indicator_period_actual_document_link_description_narrative',
                result_indicator_period_actual_document_link_description_narrative,
                representation
            )
            self.set_field(
                'result_indicator_period_actual_document_link_description_narrative_lang',
                result_indicator_period_actual_document_link_description_narrative_lang,
                representation
            )
            self.set_field(
                'result_indicator_period_actual_document_link_description_narrative_text',
                result_indicator_period_actual_document_link_description_narrative_text,
                representation
            )
            self.set_field(
                'result_indicator_period_actual_document_link_category_code',
                result_indicator_period_actual_document_link_category_code,
                representation
            )
            self.set_field(
                'result_indicator_period_actual_document_link_language_code',
                result_indicator_period_actual_document_link_language_code,
                representation
            )
            self.set_field(
                'result_indicator_period_actual_document_link_document_date_iso_date',
                result_indicator_period_actual_document_link_document_date_iso_date,
                representation
            )

    def crs_add(self, activity, representation):
        crs_add_all = activity.crsadd_set.all()
        if crs_add_all:
            crs_add_list = list()
            crs_add_other_flags_code = list()
            crs_add_other_flags_significance = list()
            crs_add_loan_terms_rate_1 = list()
            crs_add_loan_terms_rate_2 = list()
            crs_add_loan_terms_repayment_type_code = list()
            crs_add_loan_terms_repayment_plan_code = list()
            crs_add_loan_terms_commitment_date_iso_date = list()
            crs_add_loan_terms_repayment_first_date_iso_date = list()
            crs_add_loan_terms_repayment_final_date_iso_date = list()
            crs_add_loan_status_year = list()
            crs_add_loan_status_currency = list()
            crs_add_loan_status_value_date = list()
            crs_add_loan_status_interest_received = list()
            crs_add_loan_status_principal_outstanding = list()
            crs_add_loan_status_principal_arrears = list()
            crs_add_loan_status_interest_arrears = list()
            crs_add_channel_code = list()

            for crs_add in crs_add_all:
                crs_add_list.append(CrsAddSerializer(crs_add).data)

                self.add_to_list(
                    crs_add_channel_code,
                    crs_add.channel_code_id
                )

                for crs_add_other_flag in crs_add.other_flags.all():
                    self.add_to_list(
                        crs_add_other_flags_code,
                        crs_add_other_flag.other_flags_id
                    )
                    self.add_to_list(
                        crs_add_other_flags_significance,
                        crs_add_other_flag.significance
                    )

                try:
                    self.add_to_list(
                        crs_add_loan_terms_rate_1,
                        crs_add.loan_terms.rate_1
                    )
                    self.add_to_list(
                        crs_add_loan_terms_rate_2,
                        crs_add.loan_terms.rate_2
                    )
                    self.add_to_list(
                        crs_add_loan_terms_repayment_type_code,
                        crs_add.loan_terms.repayment_type_id
                    )
                    self.add_to_list(
                        crs_add_loan_terms_repayment_plan_code,
                        crs_add.loan_terms.repayment_plan_id
                    )
                    self.add_to_list(
                        crs_add_loan_terms_commitment_date_iso_date,
                        str(crs_add.loan_terms.commitment_date.strftime(
                            "%Y-%m-%d")) if crs_add.loan_terms.commitment_date else None
                    )
                    self.add_to_list(
                        crs_add_loan_terms_repayment_first_date_iso_date,
                        str(crs_add.loan_terms.repayment_first_date.strftime(
                            "%Y-%m-%d")) if crs_add.loan_terms.repayment_first_date else None
                    )
                    self.add_to_list(
                        crs_add_loan_terms_repayment_final_date_iso_date,
                        str(crs_add.loan_terms.repayment_final_date.strftime(
                            "%Y-%m-%d")) if crs_add.loan_terms.repayment_final_date else None
                    )
                except CrsAddLoanTerms.DoesNotExist:
                    pass

                try:
                    self.add_to_list(
                        crs_add_loan_status_year,
                        crs_add.loan_status.year
                    )
                    self.add_to_list(
                        crs_add_loan_status_currency,
                        crs_add.loan_status.currency_id
                    )
                    self.add_to_list(
                        crs_add_loan_status_value_date,
                        str(crs_add.loan_status.value_date.strftime(
                            "%Y-%m-%d")) if crs_add.loan_status.value_date else None
                    )
                    self.add_to_list(
                        crs_add_loan_status_interest_received,
                        crs_add.loan_status.interest_received
                    )
                    self.add_to_list(
                        crs_add_loan_status_principal_outstanding,
                        crs_add.loan_status.principal_outstanding
                    )
                    self.add_to_list(
                        crs_add_loan_status_principal_arrears,
                        crs_add.loan_status.principal_arrears
                    )
                    self.add_to_list(
                        crs_add_loan_status_interest_arrears,
                        crs_add.loan_status.interest_arrears
                    )
                except CrsAddLoanStatus.DoesNotExist:
                    pass

            self.set_field(
                'crs_add',
                json.dumps(crs_add_list),
                representation
            )
            self.set_field(
                'crs_add_other_flags_code',
                crs_add_other_flags_code,
                representation
            )
            self.set_field(
                'crs_add_other_flags_significance',
                crs_add_other_flags_significance,
                representation
            )
            self.set_field(
                'crs_add_loan_terms_rate_1',
                crs_add_loan_terms_rate_1,
                representation
            )
            self.set_field(
                'crs_add_loan_terms_rate_2',
                crs_add_loan_terms_rate_2,
                representation
            )
            self.set_field(
                'crs_add_loan_terms_repayment_type_code',
                crs_add_loan_terms_repayment_type_code,
                representation
            )
            self.set_field(
                'crs_add_loan_terms_repayment_plan_code',
                crs_add_loan_terms_repayment_plan_code,
                representation
            )
            self.set_field(
                'crs_add_loan_terms_commitment_date_iso_date',
                crs_add_loan_terms_commitment_date_iso_date,
                representation
            )
            self.set_field(
                'crs_add_loan_terms_repayment_first_date_iso_date',
                crs_add_loan_terms_repayment_first_date_iso_date,
                representation
            )
            self.set_field(
                'crs_add_loan_terms_repayment_final_date_iso_date',
                crs_add_loan_terms_repayment_final_date_iso_date,
                representation
            )
            self.set_field(
                'crs_add_loan_status_year',
                crs_add_loan_status_year,
                representation
            )
            self.set_field(
                'crs_add_loan_status_currency',
                crs_add_loan_status_currency,
                representation
            )
            self.set_field(
                'crs_add_loan_status_value_date',
                crs_add_loan_status_value_date,
                representation
            )
            self.set_field(
                'crs_add_loan_status_interest_received',
                crs_add_loan_status_interest_received,
                representation
            )
            self.set_field(
                'crs_add_loan_status_principal_outstanding',
                crs_add_loan_status_principal_outstanding,
                representation
            )
            self.set_field(
                'crs_add_loan_status_principal_arrears',
                crs_add_loan_status_principal_arrears,
                representation
            )
            self.set_field(
                'crs_add_loan_status_interest_arrears',
                crs_add_loan_status_interest_arrears,
                representation
            )
            self.set_field(
                'crs_add_channel_code',
                crs_add_channel_code,
                representation
            )

    def fss(self, activity, representation):
        fss_all = activity.fss_set.all()
        if fss_all:
            fss_list = list()
            fss_extraction_date = list()
            fss_priority = list()
            fss_phaseout_year = list()

            fss_forecast_year = list()
            fss_forecast_value_date = list()
            fss_forecast_currency = list()
            fss_forecast_value = list()

            for fss in fss_all:
                self.add_to_list(
                    fss_extraction_date,
                    str(fss.extraction_date.strftime(
                        "%Y-%m-%d")) if fss.extraction_date else None
                )
                self.add_to_list(
                    fss_priority,
                    '1' if fss.priority else '0'
                )
                self.add_to_list(
                    fss_phaseout_year,
                    fss.phaseout_year
                )

                for forecast in fss.fssforecast_set.all():
                    self.add_to_list(
                        fss_forecast_year,
                        forecast.year
                    )
                    self.add_to_list(
                        fss_forecast_value_date,
                        str(forecast.value_date.strftime(
                            "%Y-%m-%d")) if forecast.value_date else None
                    )
                    self.add_to_list(
                        fss_forecast_currency,
                        forecast.currency_id
                    )
                    self.add_to_list(
                        fss_forecast_value,
                        str(forecast.value)
                    )

            self.set_field(
                'fss_extraction_date',
                fss_extraction_date,
                representation
            )
            self.set_field(
                'fss_priority',
                fss_priority,
                representation
            )
            self.set_field(
                'fss_phaseout_year',
                fss_phaseout_year,
                representation
            )
            self.set_field(
                'fss_forecast_year',
                fss_forecast_year,
                representation
            )
            self.set_field(
                'fss_forecast_value_date',
                fss_forecast_value_date,
                representation
            )
            self.set_field(
                'fss_forecast_currency',
                fss_forecast_currency,
                representation
            )
            self.set_field(
                'fss_forecast_value',
                fss_forecast_value,
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
        self.contact_info(activity=activity, representation=representation)
        self.recipient_country(activity=activity, representation=representation)
        self.recipient_region(activity=activity, representation=representation)
        self.location(activity=activity, representation=representation)
        self.sector(activity=activity, representation=representation)
        self.country_budget_items(activity=activity, representation=representation)
        self.humanitarian_scope(activity=activity, representation=representation)
        self.policy_marker(activity=activity, representation=representation)
        self.budget(activity=activity, representation=representation)
        self.planned_disbursement(activity=activity, representation=representation)
        self.transaction(activity=activity, representation=representation)
        self.document_link(activity=activity, representation=representation)
        self.conditions(activity=activity, representation=representation)
        self.result(activity=activity, representation=representation)
        self.crs_add(activity=activity, representation=representation)
        self.fss(activity=activity, representation=representation)

        return representation
