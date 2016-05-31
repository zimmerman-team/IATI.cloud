from django.db.models.fields import FieldDoesNotExist
from django.db.models.fields.related import ForeignObjectRel
from django.db.models.fields.related import OneToOneRel
from django.db.models import Q
from django.conf import settings

from django_filters import FilterSet
from django_filters import NumberFilter
from django_filters import DateFilter
from django_filters import BooleanFilter

from api.generics.filters import CommaSeparatedCharFilter
from api.generics.filters import CommaSeparatedCharMultipleFilter
from api.generics.filters import TogetherFilterSet
from api.generics.filters import ToManyFilter
from api.generics.filters import NestedFilter

from rest_framework import filters

from iati.models import *
from iati.transaction.models import *


class ActivityFilter(TogetherFilterSet):

    activity_id = CommaSeparatedCharFilter(
        name='id',
        lookup_type='in')

    activity_scope = CommaSeparatedCharFilter(
        name='scope__code',
        lookup_type='in',)

    document_link_category = CommaSeparatedCharFilter(
        lookup_type='in',
        name='documentlink__categories')

    planned_start_date_lte = DateFilter(
        lookup_type='lte',
        name='planned_start')

    planned_start_date_gte = DateFilter(
        lookup_type='gte',
        name='planned_start')

    actual_start_date_lte = DateFilter(
        lookup_type='lte',
        name='actual_start')

    actual_start_date_gte = DateFilter(
        lookup_type='gte',
        name='actual_start')

    planned_end_date_lte = DateFilter(
        lookup_type='lte',
        name='planned_end')

    planned_end_date_gte = DateFilter(
        lookup_type='gte',
        name='planned_end')

    actual_end_date_lte = DateFilter(
        lookup_type='lte',
        name='actual_end')

    actual_end_date_gte = DateFilter(
        lookup_type='gte',
        name='actual_end')

    end_date_lte = DateFilter(
        lookup_type='lte',
        name='end_date')

    end_date_gte = DateFilter(
        lookup_type='gte',
        name='end_date')

    start_date_lte = DateFilter(
        lookup_type='lte',
        name='start_date')

    start_date_gte = DateFilter(
        lookup_type='gte',
        name='start_date')

    end_date_isnull = BooleanFilter(lookup_type='isnull', name='end_date')
    start_date_isnull = BooleanFilter(lookup_type='isnull', name='start_date')

    xml_source_ref = CommaSeparatedCharFilter(
        lookup_type='in',
        name='xml_source_ref',)

    activity_status = CommaSeparatedCharFilter(
        lookup_type='in',
        name='activity_status',)

    hierarchy = CommaSeparatedCharFilter(
        lookup_type='in',
        name='hierarchy',)

    collaboration_type = CommaSeparatedCharFilter(
        lookup_type='in',
        name='collaboration_type',)

    default_flow_type = CommaSeparatedCharFilter(
        lookup_type='in',
        name='default_flow_type',)

    default_aid_type = CommaSeparatedCharFilter(
        lookup_type='in',
        name='default_aid_type',)

    default_finance_type = CommaSeparatedCharFilter(
        lookup_type='in',
        name='default_finance_type',)

    default_tied_status = CommaSeparatedCharFilter(
        lookup_type='in',
        name='default_tied_status',)

    budget_period_start = DateFilter(
        lookup_type='gte',
        name='budget__period_start',)

    budget_period_end = DateFilter(
        lookup_type='lte',
        name='budget__period_end')

    related_activity_id = ToManyFilter(
        qs=RelatedActivity,
        fk='current_activity',
        lookup_type='in',
        name='ref_activity__id',
    )

    related_activity_type = ToManyFilter(
        qs=RelatedActivity,
        lookup_type='in',
        name='type__code',
        fk='current_activity',
    )

    related_activity_recipient_country = ToManyFilter(
        qs=RelatedActivity,
        lookup_type='in',
        name='ref_activity__recipient_country',
        fk='current_activity',
    )

    related_activity_recipient_region = ToManyFilter(
        qs=RelatedActivity,
        lookup_type='in',
        name='ref_activity__recipient_region',
        fk='current_activity',
    )

    related_activity_sector = ToManyFilter(
        qs=RelatedActivity,
        lookup_type='in',
        name='ref_activity__sector',
        fk='current_activity',
    )

    related_activity_sector_category = ToManyFilter(
        qs=RelatedActivity,
        lookup_type='in',
        name='ref_activity__sector__category',
        fk='current_activity',
    )

    budget_currency = ToManyFilter(
        qs=Budget,
        lookup_type='in',
        name='currency__code',
        fk='activity',
    )

    recipient_country = ToManyFilter(
        qs=ActivityRecipientCountry,
        lookup_type='in',
        name='country__code',
        fk='activity',
    )

    recipient_region = ToManyFilter(
        qs=ActivityRecipientRegion,
        lookup_type='in',
        name='region__code',
        fk='activity',
    )
    sector = ToManyFilter(
        qs=ActivitySector,
        lookup_type='in',
        name='sector__code',
        fk='activity',
    )

    sector_category = ToManyFilter(
        qs=ActivitySector,
        lookup_type='in',
        name='sector__category__code',
        fk='activity',
    )

    participating_organisation = ToManyFilter(
        qs=ActivityParticipatingOrganisation,
        lookup_type='in',
        name='normalized_ref',
        fk='activity',
    )

    participating_organisation_name = ToManyFilter(
        qs=ActivityParticipatingOrganisation,
        lookup_type='in',
        name='primary_name',
        fk='activity',
    )

    participating_organisation_role = ToManyFilter(
        qs=ActivityParticipatingOrganisation,
        lookup_type='in',
        name='role__code',
        fk='activity',
    )

    participating_organisation_type = ToManyFilter(
        qs=ActivityParticipatingOrganisation,
        lookup_type='in',
        name='type__code',
        fk='activity',
    )

    reporting_organisation = ToManyFilter(
        qs=ActivityReportingOrganisation,
        lookup_type='in',
        name='organisation__organisation_identifier',
        fk='activity',
    )

    reporting_organisation_startswith = ToManyFilter(
        qs=ActivityReportingOrganisation,
        lookup_type='startswith',
        name='organisation__organisation_identifier',
        fk='activity',
    )

    #
    # Transaction filters
    #

    transaction_type = ToManyFilter(
        qs=Transaction,
        lookup_type='in',
        name='transaction_type',
        fk='activity',
    )

    provider_organisation_primary_name = ToManyFilter(
        qs=Transaction,
        lookup_type='in',
        name='provider_organisation__primary_name',
        fk='activity',
    )

    receiver_organisation_primary_name = ToManyFilter(
        qs=Transaction,
        lookup_type='in',
        name='receiver_organisation__primary_name',
        fk='activity',
    )

    transaction_provider_organisation_name = ToManyFilter(
        qs=Transaction,
        lookup_type='in',
        name='provider_organisation__narratives__content',
        fk='activity',
    )

    transaction_receiver_organisation_name = ToManyFilter(
        qs=Transaction,
        lookup_type='in',
        name='receiver_organisation__narratives__content',
        fk='activity',
    )

    transaction_provider_activity = ToManyFilter(
        qs=Transaction,
        lookup_type='in',
        name='provider_organisation__provider_activity_ref',
        fk='activity',
    )

    transaction_currency = ToManyFilter(
        qs=Transaction,
        lookup_type='in',
        name='currency',
        fk='activity',
    )

    transaction_date_year = ToManyFilter(
        qs=Transaction,
        lookup_type='year',
        name='transaction_date',
        fk='activity'
    )

    #
    # Aggregated values filters
    #

    total_budget_lte = NumberFilter(
        lookup_type='lte',
        name='activity_aggregation__budget_value')

    total_budget_gte = NumberFilter(
        lookup_type='gte',
        name='activity_aggregation__budget_value')

    total_disbursement_lte = NumberFilter(
        lookup_type='lte',
        name='activity_aggregation__disbursement_value')

    total_disbursement_gte = NumberFilter(
        lookup_type='gte',
        name='activity_aggregation__disbursement_value')

    total_incoming_funds_lte = NumberFilter(
        lookup_type='lte',
        name='activity_aggregation__incoming_funds_value')

    total_incoming_funds_gte = NumberFilter(
        lookup_type='gte',
        name='activity_aggregation__incoming_funds_value')

    total_expenditure_lte = NumberFilter(
        lookup_type='lte',
        name='activity_aggregation__expenditure_value')

    total_expenditure_gte = NumberFilter(
        lookup_type='gte',
        name='activity_aggregation__expenditure_value')

    total_commitment_lte = NumberFilter(
        lookup_type='lte',
        name='activity_aggregation__commitment_value')

    total_commitment_gte = NumberFilter(
        lookup_type='gte',
        name='activity_aggregation__commitment_value')

    total_hierarchy_budget_lte = NumberFilter(
        lookup_type='lte',
        name='activity_plus_child_aggregation__budget_value')

    total_hierarchy_budget_gte = NumberFilter(
        lookup_type='gte',
        name='activity_plus_child_aggregation__budget_value')

    total_hierarchy_disbursement_lte = NumberFilter(
        lookup_type='lte',
        name='activity_plus_child_aggregation__disbursement_value')

    total_hierarchy_disbursement_gte = NumberFilter(
        lookup_type='gte',
        name='activity_plus_child_aggregation__disbursement_value')

    total_hierarchy_incoming_funds_lte = NumberFilter(
        lookup_type='lte',
        name='activity_plus_child_aggregation__incoming_funds_value')

    total_hierarchy_incoming_funds_gte = NumberFilter(
        lookup_type='gte',
        name='activity_plus_child_aggregation__incoming_funds_value')

    total_hierarchy_expenditure_lte = NumberFilter(
        lookup_type='lte',
        name='activity_plus_child_aggregation__expenditure_value')

    total_hierarchy_expenditure_gte = NumberFilter(
        lookup_type='gte',
        name='activity_plus_child_aggregation__expenditure_value')

    total_hierarchy_commitment_lte = NumberFilter(
        lookup_type='lte',
        name='activity_plus_child_aggregation__commitment_value')

    total_hierarchy_commitment_gte = NumberFilter(
        lookup_type='gte',
        name='activity_plus_child_aggregation__commitment_value')

    class Meta:
        model = Activity
        together_exclusive = [('budget_period_start', 'budget_period_end')]


class RelatedActivityFilter(FilterSet):

    related_activity_type = CommaSeparatedCharFilter(
        lookup_type='in',
        name='type__code')

    class Meta:
        model = RelatedActivity


class RelatedOrderingFilter(filters.OrderingFilter):
    """
    Extends OrderingFilter to support ordering by fields in related models
    using the Django ORM __ notation

    Also provides support for mapping of fields,
    in remove_invalid_fields a mapping is maintained
    to make 'user-friendly' names possible
    """

    def get_ordering(self, request, queryset, view):
        ordering = super(RelatedOrderingFilter, self).get_ordering(request, queryset, view)

        always_ordering = getattr(view, 'always_ordering', None)

        if ordering and always_ordering:
            ordering = ordering + [always_ordering] 
            queryset.distinct(always_ordering)

        return ordering

    def filter_queryset(self, request, queryset, view):

        ordering = self.get_ordering(request, queryset, view)

        if ordering: 
            ordering = [order.replace("-", "") for order in ordering]
            queryset = queryset.distinct(*ordering)

        return super(RelatedOrderingFilter, self).filter_queryset(request, queryset, view)

    def is_valid_field(self, model, field):
        """
        Return true if the field exists within the model (or in the related
        model specified using the Django ORM __ notation)
        """
        components = field.split('__', 1)
        try:
            field, parent_model, direct, m2m = model._meta.get_field_by_name(components[0])

            if isinstance(field, OneToOneRel):
                return self.is_valid_field(field.related_model, components[1])

            # reverse relation
            if isinstance(field, ForeignObjectRel):
                return self.is_valid_field(field.model, components[1])

            # foreign key
            if field.rel and len(components) == 2:
                return self.is_valid_field(field.rel.to, components[1])
            return True
        except FieldDoesNotExist:
            return False

    def remove_invalid_fields(self, queryset, ordering, view):

        mapped_fields = {
            'title': 'title__narratives__content',
            'activity_budget_value': 'activity_aggregation__budget_value',
            'activity_incoming_funds_value': 'activity_aggregation__incoming_funds_value',
            'activity_disbursement_value': 'activity_aggregation__disbursement_value',
            'activity_expenditure_value': 'activity_aggregation__expenditure_value',
            'activity_plus_child_budget_value': 'activity_plus_child_aggregation__budget_value',
            'planned_start_date': 'planned_start',
            'actual_start_date': 'actual_start',
            'planned_end_date': 'planned_end',
            'actual_end_date': 'actual_end',
            'start_date': 'start_date',
            'end_date': 'end_date',
        }

        for i, term in enumerate(ordering):
            if term.lstrip('-') in mapped_fields:
                ordering[i] = ordering[i].replace(term.lstrip('-'), mapped_fields[term.lstrip('-')])

        return [term for term in ordering
                if self.is_valid_field(queryset.model, term.lstrip('-'))]
