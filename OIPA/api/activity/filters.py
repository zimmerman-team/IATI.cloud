from django.db.models.fields import FieldDoesNotExist
from django.db.models.fields.related import ForeignObjectRel
from django.db.models.fields.related import OneToOneRel
from django.db.models import Q

from django_filters import FilterSet, NumberFilter, DateFilter, BooleanFilter

from api.generics.filters import CommaSeparatedCharFilter
from api.generics.filters import CommaSeparatedCharMultipleFilter
from api.generics.filters import TogetherFilterSet
from iati.models import Activity, RelatedActivity

from rest_framework import filters
from common.util import combine_filters
from djorm_pgfulltext.fields import TSConfig


class SearchFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):

        query = request.query_params.get('q', None)

        if query:

            query_fields = request.query_params.get('q_fields')
            dict_query_list = [TSConfig('simple'), query]

            if query_fields:

                query_fields = query_fields.split(',')

                if isinstance(query_fields, list):
                    filters = combine_filters([Q(**{'activitysearch__{}__ft'.format(field): dict_query_list}) for field in query_fields])
                    return queryset.filter(filters)

            else:

                return queryset.filter(activitysearch__text__ft=dict_query_list)

        return queryset


class ActivityFilter(TogetherFilterSet):

    activity_id = CommaSeparatedCharFilter(
        name='id',
        lookup_type='in')

    activity_scope = CommaSeparatedCharFilter(
        name='scope__code',
        lookup_type='in',)

    recipient_country = CommaSeparatedCharFilter(
        lookup_type='in',
        name='recipient_country',)

    recipient_region = CommaSeparatedCharFilter(
        lookup_type='in',
        name='recipient_region',)

    recipient_region_not_in = CommaSeparatedCharFilter(
        lookup_type='in',
        name='recipient_region',
        exclude=True,)

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

    end_date_isnull = BooleanFilter(name='end_date__isnull')
    start_date_isnull = BooleanFilter(name='start_date__isnull')

    sector = CommaSeparatedCharFilter(
        lookup_type='in',
        name='sector',)

    sector_category = CommaSeparatedCharFilter(
        lookup_type='in',
        name='activitysector__sector__category__code',)

    participating_organisation = CommaSeparatedCharFilter(
        lookup_type='in',
        name='participating_organisations__normalized_ref',)

    participating_organisation_name = CommaSeparatedCharFilter(
        lookup_type='in',
        name='participating_organisations__primary_name',)

    participating_organisation_role = CommaSeparatedCharFilter(
        lookup_type='in',
        name='participating_organisations__role__code',)

    reporting_organisation = CommaSeparatedCharFilter(
        lookup_type='in',
        name='reporting_organisations__normalized_ref')

    reporting_organisation_startswith = CommaSeparatedCharMultipleFilter(
        lookup_type='startswith',
        name='reporting_organisations__normalized_ref')

    xml_source_ref = CommaSeparatedCharFilter(
        lookup_type='in',
        name='xml_source_ref',)

    activity_status = CommaSeparatedCharFilter(
        lookup_type='in',
        name='activity_status',)

    hierarchy = CommaSeparatedCharFilter(
        lookup_type='in',
        name='hierarchy',)

    related_activity_id = CommaSeparatedCharFilter(
        lookup_type='in', name='relatedactivity__ref_activity__id', )

    related_activity_type = CommaSeparatedCharFilter(
        lookup_type='in',
        name='relatedactivity__type__code',)

    related_activity_recipient_country = CommaSeparatedCharFilter(
        lookup_type='in',
        name='relatedactivity__ref_activity__recipient_country',)

    related_activity_recipient_region = CommaSeparatedCharFilter(
        lookup_type='in',
        name='relatedactivity__ref_activity__recipient_region',)

    related_activity_sector = CommaSeparatedCharFilter(
        lookup_type='in',
        name='relatedactivity__ref_activity__sector',)

    related_activity_sector_category = CommaSeparatedCharFilter(
        lookup_type='in',
        name='relatedactivity__ref_activity__sector__category',)

    budget_period_start = DateFilter(
        lookup_type='gte',
        name='budget__period_start',)

    budget_period_end = DateFilter(
        lookup_type='lte',
        name='budget__period_end')

    budget_currency = CommaSeparatedCharFilter(
        lookup_type='in',
        name='budget__currency__code')

    transaction_provider_organisation_name = CommaSeparatedCharFilter(
        lookup_type='in',
        name='transaction__provider_organisation__narratives__content')

    transaction_receiver_organisation_name = CommaSeparatedCharFilter(
        lookup_type='in',
        name='transaction__receiver_organisation__narratives__content')

    transaction_type = CommaSeparatedCharFilter(
        lookup_type='in',
        name='transaction__transaction_type')

    transaction_provider_activity = CommaSeparatedCharFilter(
        lookup_type='in',
        name='transaction__provider_organisation__provider_activity_ref',)

    transaction_date_year = NumberFilter(
        lookup_type='year',
        name='transaction__transaction_date',)

    activity_aggregation_budget_value_lte = NumberFilter(
        lookup_type='lte',
        name='activity_aggregation__budget_value')

    activity_aggregation_budget_value_gte = NumberFilter(
        lookup_type='gte',
        name='activity_aggregation__budget_value')

    activity_aggregation_disbursement_value_lte = NumberFilter(
        lookup_type='lte',
        name='activity_aggregation__disbursement_value')

    activity_aggregation_disbursement_value_gte = NumberFilter(
        lookup_type='gte',
        name='activity_aggregation__disbursement_value')

    activity_aggregation_incoming_fund_value_lte = NumberFilter(
        lookup_type='lte',
        name='activity_aggregation__incoming_funds_value')

    activity_aggregation_incoming_fund_value_gte = NumberFilter(
        lookup_type='gte',
        name='activity_aggregation__incoming_funds_value')

    activity_aggregation_expenditure_value_lte = NumberFilter(
        lookup_type='lte',
        name='activity_aggregation__expenditure_value')

    activity_aggregation_expenditure_value_gte = NumberFilter(
        lookup_type='gte',
        name='activity_aggregation__expenditure_value')

    activity_aggregation_commitment_value_lte = NumberFilter(
        lookup_type='lte',
        name='activity_aggregation__commitment_value')

    activity_aggregation_commitment_value_gte = NumberFilter(
        lookup_type='gte',
        name='activity_aggregation__commitment_value')



    activity_plus_child_aggregation_budget_value_lte = NumberFilter(
        lookup_type='lte',
        name='activity_plus_child_aggregation__budget_value')

    activity_plus_child_aggregation_budget_value_gte = NumberFilter(
        lookup_type='gte',
        name='activity_plus_child_aggregation__budget_value')

    activity_plus_child_aggregation_disbursement_value_lte = NumberFilter(
        lookup_type='lte',
        name='activity_plus_child_aggregation__disbursement_value')

    activity_plus_child_aggregation_disbursement_value_gte = NumberFilter(
        lookup_type='gte',
        name='activity_plus_child_aggregation__disbursement_value')

    activity_plus_child_aggregation_incoming_fund_value_lte = NumberFilter(
        lookup_type='lte',
        name='activity_plus_child_aggregation__incoming_funds_value')

    activity_plus_child_aggregation_incoming_fund_value_gte = NumberFilter(
        lookup_type='gte',
        name='activity_plus_child_aggregation__incoming_funds_value')

    activity_plus_child_aggregation_expenditure_value_lte = NumberFilter(
        lookup_type='lte',
        name='activity_plus_child_aggregation__expenditure_value')

    activity_plus_child_aggregation_expenditure_value_gte = NumberFilter(
        lookup_type='gte',
        name='activity_plus_child_aggregation__expenditure_value')

    activity_plus_child_aggregation_commitment_value_lte = NumberFilter(
        lookup_type='lte',
        name='activity_plus_child_aggregation__commitment_value')

    activity_plus_child_aggregation_commitment_value_gte = NumberFilter(
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
