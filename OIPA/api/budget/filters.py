from django.db.models.fields import FieldDoesNotExist
from django.db.models.fields.related import ForeignObjectRel
from django.db.models.fields.related import OneToOneRel

from django_filters import FilterSet
from django_filters import NumberFilter
from django_filters import DateFilter
from django_filters import BooleanFilter

from api.generics.filters import CommaSeparatedCharFilter
from api.generics.filters import TogetherFilterSet
from api.generics.filters import ToManyFilter

from rest_framework import filters

from iati.models import *
from iati.transaction.models import *


class BudgetFilter(TogetherFilterSet):

    activity_id = CommaSeparatedCharFilter(
        name='activity__id',
        lookup_type='in')

    activity_scope = CommaSeparatedCharFilter(
        name='activity__scope__code',
        lookup_type='in',)

    document_link_category = CommaSeparatedCharFilter(
        lookup_type='in',
        name='documentlink__categories')

    planned_start_date_lte = DateFilter(
        lookup_type='lte',
        name='activity__planned_start')

    planned_start_date_gte = DateFilter(
        lookup_type='gte',
        name='activity__planned_start')

    actual_start_date_lte = DateFilter(
        lookup_type='lte',
        name='activity__actual_start')

    actual_start_date_gte = DateFilter(
        lookup_type='gte',
        name='activity__actual_start')

    planned_end_date_lte = DateFilter(
        lookup_type='lte',
        name='activity__planned_end')

    planned_end_date_gte = DateFilter(
        lookup_type='gte',
        name='activity__planned_end')

    actual_end_date_lte = DateFilter(
        lookup_type='lte',
        name='activity__actual_end')

    actual_end_date_gte = DateFilter(
        lookup_type='gte',
        name='activity__actual_end')

    end_date_lte = DateFilter(
        lookup_type='lte',
        name='activity__end_date')

    end_date_gte = DateFilter(
        lookup_type='gte',
        name='activity__end_date')

    start_date_lte = DateFilter(
        lookup_type='lte',
        name='activity__start_date')

    start_date_gte = DateFilter(
        lookup_type='gte',
        name='activity__start_date')

    end_date_isnull = BooleanFilter(
        lookup_type='isnull', 
        name='activity__end_date')
    start_date_isnull = BooleanFilter(
        lookup_type='isnull', 
        name='activity__start_date')

    xml_source_ref = CommaSeparatedCharFilter(
        lookup_type='in',
        name='activity__xml_source_ref',)

    activity_status = CommaSeparatedCharFilter(
        lookup_type='in',
        name='activity__activity_status',)

    hierarchy = CommaSeparatedCharFilter(
        lookup_type='in',
        name='activity__hierarchy',)

    collaboration_type = CommaSeparatedCharFilter(
        lookup_type='in',
        name='activity__collaboration_type',)

    default_flow_type = CommaSeparatedCharFilter(
        lookup_type='in',
        name='activity__default_flow_type',)

    default_aid_type = CommaSeparatedCharFilter(
        lookup_type='in',
        name='activity__default_aid_type',)

    default_finance_type = CommaSeparatedCharFilter(
        lookup_type='in',
        name='activity__default_finance_type',)

    default_tied_status = CommaSeparatedCharFilter(
        lookup_type='in',
        name='activity__default_tied_status',)

    budget_period_start = DateFilter(
        lookup_type='gte',
        name='period_start',)

    budget_period_end = DateFilter(
        lookup_type='lte',
        name='period_end')

    related_activity_recipient_country = ToManyFilter(
        main_fk='activity',
        qs=RelatedActivity,
        lookup_type='in',
        name='ref_activity__recipient_country',
        fk='current_activity',)

    related_activity_id = ToManyFilter(
        main_fk='activity',
        qs=RelatedActivity,
        lookup_type='in',
        name='ref_activity__id',
        fk='current_activity',)

    related_activity_type = ToManyFilter(
        main_fk='activity',
        qs=RelatedActivity,
        lookup_type='in',
        name='type__code',
        fk='current_activity',)

    related_activity_recipient_country = ToManyFilter(
        main_fk='activity',
        qs=RelatedActivity,
        lookup_type='in',
        name='ref_activity__recipient_country',
        fk='current_activity',)

    related_activity_recipient_region = ToManyFilter(
        main_fk='activity',
        qs=RelatedActivity,
        lookup_type='in',
        name='ref_activity__recipient_region',
        fk='current_activity',)

    related_activity_sector = ToManyFilter(
        main_fk='activity',
        qs=RelatedActivity,
        lookup_type='in',
        name='ref_activity__sector',
        fk='current_activity',)

    related_activity_sector_category = ToManyFilter(
        main_fk='activity',
        qs=RelatedActivity,
        lookup_type='in',
        name='ref_activity__sector__category',
        fk='current_activity',)

    budget_currency = ToManyFilter(
        qs=Budget,
        lookup_type='in',
        name='currency__code',
        fk='activity__budget',
    )

    recipient_country = ToManyFilter(
        qs=ActivityRecipientCountry,
        lookup_type='in',
        name='country__code',
        fk='activity__budget',
    )

    recipient_region = ToManyFilter(
        qs=ActivityRecipientRegion,
        lookup_type='in',
        name='region__code',
        fk='activity__budget',
    )
    sector = ToManyFilter(
        qs=ActivitySector,
        lookup_type='in',
        name='sector__code',
        fk='activity__budget',
    )

    sector_vocabulary = ToManyFilter(
        qs=ActivitySector,
        lookup_type='in',
        name='sector__vocabulary__code',
        fk='activity__budget',
    )

    sector_category = ToManyFilter(
        qs=ActivitySector,
        lookup_type='in',
        name='sector__category__code',
        fk='activity__budget',
    )

    participating_organisation = ToManyFilter(
        qs=ActivityParticipatingOrganisation,
        lookup_type='in',
        name='normalized_ref',
        fk='activity__budget',
    )

    participating_organisation_name = ToManyFilter(
        qs=ActivityParticipatingOrganisation,
        lookup_type='in',
        name='primary_name',
        fk='activity__budget',
    )

    participating_organisation_role = ToManyFilter(
        qs=ActivityParticipatingOrganisation,
        lookup_type='in',
        name='role__code',
        fk='activity__budget',
    )

    participating_organisation_type = ToManyFilter(
        qs=ActivityParticipatingOrganisation,
        lookup_type='in',
        name='type__code',
        fk='activity__budget',
    )

    reporting_organisation = ToManyFilter(
        qs=ActivityReportingOrganisation,
        lookup_type='in',
        name='normalized_ref',
        fk='activity__budget',
    )

    reporting_organisation_startswith = ToManyFilter(
        qs=ActivityReportingOrganisation,
        lookup_type='startswith',
        name='normalized_ref',
        fk='activity__budget',
    )

    indicator_title = ToManyFilter(
        qs=ResultIndicatorTitle,
        lookup_type='in',
        name='primary_name',
        fk='result_indicator__result__activity__budget')

    #
    # Transaction filters
    #

    transaction_type = ToManyFilter(
        qs=Transaction,
        lookup_type='in',
        name='transaction_type',
        fk='activity__budget',
    )

    provider_organisation_primary_name = ToManyFilter(
        qs=Transaction,
        lookup_type='in',
        name='provider_organisation__primary_name',
        fk='activity__budget',
    )

    receiver_organisation_primary_name = ToManyFilter(
        qs=Transaction,
        lookup_type='in',
        name='receiver_organisation__primary_name',
        fk='activity__budget',
    )

    transaction_provider_organisation_name = ToManyFilter(
        qs=Transaction,
        lookup_type='in',
        name='provider_organisation__narratives__content',
        fk='activity__budget',
    )

    transaction_receiver_organisation_name = ToManyFilter(
        qs=Transaction,
        lookup_type='in',
        name='receiver_organisation__narratives__content',
        fk='activity__budget',
    )

    transaction_provider_activity = ToManyFilter(
        qs=Transaction,
        lookup_type='in',
        name='provider_organisation__provider_activity_ref',
        fk='activity__budget',
    )

    transaction_currency = ToManyFilter(
        qs=Transaction,
        lookup_type='in',
        name='currency',
        fk='activity__budget',
    )

    transaction_date_year = ToManyFilter(
        qs=Transaction,
        lookup_type='year',
        name='transaction_date',
        fk='activity__budget'
    )

    #
    # Aggregated values filters
    #

    total_budget_lte = NumberFilter(
        lookup_type='lte',
        name='activity__activity_aggregation__budget_value')

    total_budget_gte = NumberFilter(
        lookup_type='gte',
        name='activity__activity_aggregation__budget_value')

    total_disbursement_lte = NumberFilter(
        lookup_type='lte',
        name='activity__activity_aggregation__disbursement_value')

    total_disbursement_gte = NumberFilter(
        lookup_type='gte',
        name='activity__activity_aggregation__disbursement_value')

    total_incoming_funds_lte = NumberFilter(
        lookup_type='lte',
        name='activity__activity_aggregation__incoming_funds_value')

    total_incoming_funds_gte = NumberFilter(
        lookup_type='gte',
        name='activity__activity_aggregation__incoming_funds_value')

    total_expenditure_lte = NumberFilter(
        lookup_type='lte',
        name='activity__activity_aggregation__expenditure_value')

    total_expenditure_gte = NumberFilter(
        lookup_type='gte',
        name='activity__activity_aggregation__expenditure_value')

    total_commitment_lte = NumberFilter(
        lookup_type='lte',
        name='activity__activity_aggregation__commitment_value')

    total_commitment_gte = NumberFilter(
        lookup_type='gte',
        name='activity__activity_aggregation__commitment_value')

    total_hierarchy_budget_lte = NumberFilter(
        lookup_type='lte',
        name='activity__activity_plus_child_aggregation__budget_value')

    total_hierarchy_budget_gte = NumberFilter(
        lookup_type='gte',
        name='activity__activity_plus_child_aggregation__budget_value')

    total_hierarchy_disbursement_lte = NumberFilter(
        lookup_type='lte',
        name='activity__activity_plus_child_aggregation__disbursement_value')

    total_hierarchy_disbursement_gte = NumberFilter(
        lookup_type='gte',
        name='activity__activity_plus_child_aggregation__disbursement_value')

    total_hierarchy_incoming_funds_lte = NumberFilter(
        lookup_type='lte',
        name='activity__activity_plus_child_aggregation__incoming_funds_value')

    total_hierarchy_incoming_funds_gte = NumberFilter(
        lookup_type='gte',
        name='activity__activity_plus_child_aggregation__incoming_funds_value')

    total_hierarchy_expenditure_lte = NumberFilter(
        lookup_type='lte',
        name='activity__activity_plus_child_aggregation__expenditure_value')

    total_hierarchy_expenditure_gte = NumberFilter(
        lookup_type='gte',
        name='activity__activity_plus_child_aggregation__expenditure_value')

    total_hierarchy_commitment_lte = NumberFilter(
        lookup_type='lte',
        name='activity__activity_plus_child_aggregation__commitment_value')

    total_hierarchy_commitment_gte = NumberFilter(
        lookup_type='gte',
        name='activity__activity_plus_child_aggregation__commitment_value')

    class Meta:
        model = Budget
