from django_filters import BooleanFilter, DateFilter, NumberFilter
from api.generics.filters import (
    CommaSeparatedCharFilter, TogetherFilterSet, ToManyFilter
)
from iati.models import (
    ActivityParticipatingOrganisation, ActivityRecipientCountry,
    ActivityRecipientRegion, ActivityReportingOrganisation, ActivitySector,
    Budget, RelatedActivity, ResultIndicatorTitle
)
from iati.transaction.models import Transaction
from rest_framework import filters
from django.db.models.fields.related import ForeignObjectRel, OneToOneRel
from django.db.models.fields import FieldDoesNotExist


class BudgetFilter(TogetherFilterSet):

    activity_id = CommaSeparatedCharFilter(
        field_name='activity__iati_identifier',
        lookup_expr='in')

    activity_scope = CommaSeparatedCharFilter(
        field_name='activity__scope__code',
        lookup_expr='in',)

    document_link_category = CommaSeparatedCharFilter(
        lookup_expr='in',
        field_name='documentlink__categories')

    planned_start_date_lte = DateFilter(
        lookup_expr='lte',
        field_name='activity__planned_start')

    planned_start_date_gte = DateFilter(
        lookup_expr='gte',
        field_name='activity__planned_start')

    actual_start_date_lte = DateFilter(
        lookup_expr='lte',
        field_name='activity__actual_start')

    actual_start_date_gte = DateFilter(
        lookup_expr='gte',
        field_name='activity__actual_start')

    planned_end_date_lte = DateFilter(
        lookup_expr='lte',
        field_name='activity__planned_end')

    planned_end_date_gte = DateFilter(
        lookup_expr='gte',
        field_name='activity__planned_end')

    actual_end_date_lte = DateFilter(
        lookup_expr='lte',
        field_name='activity__actual_end')

    actual_end_date_gte = DateFilter(
        lookup_expr='gte',
        field_name='activity__actual_end')

    end_date_lte = DateFilter(
        lookup_expr='lte',
        field_name='activity__end_date')

    end_date_gte = DateFilter(
        lookup_expr='gte',
        field_name='activity__end_date')

    start_date_lte = DateFilter(
        lookup_expr='lte',
        field_name='activity__start_date')

    start_date_gte = DateFilter(
        lookup_expr='gte',
        field_name='activity__start_date')

    end_date_isnull = BooleanFilter(
        lookup_expr='isnull',
        field_name='activity__end_date')
    start_date_isnull = BooleanFilter(
        lookup_expr='isnull',
        field_name='activity__start_date')

    activity_status = CommaSeparatedCharFilter(
        lookup_expr='in',
        field_name='activity__activity_status',)

    hierarchy = CommaSeparatedCharFilter(
        lookup_expr='in',
        field_name='activity__hierarchy',)

    collaboration_type = CommaSeparatedCharFilter(
        lookup_expr='in',
        field_name='activity__collaboration_type',)

    default_flow_type = CommaSeparatedCharFilter(
        lookup_expr='in',
        field_name='activity__default_flow_type',)

    default_aid_type = CommaSeparatedCharFilter(
        lookup_expr='in',
        field_name='activity__default_aid_type',)

    default_finance_type = CommaSeparatedCharFilter(
        lookup_expr='in',
        field_name='activity__default_finance_type',)

    default_tied_status = CommaSeparatedCharFilter(
        lookup_expr='in',
        field_name='activity__default_tied_status',)

    budget_period_start = DateFilter(
        lookup_expr='gte',
        field_name='period_start',)

    budget_period_end = DateFilter(
        lookup_expr='lte',
        field_name='period_end')

    related_activity_recipient_country = ToManyFilter(
        main_fk='activity',
        qs=RelatedActivity,
        lookup_expr='in',
        field_name='ref_activity__recipient_country',
        fk='current_activity',)

    related_activity_id = ToManyFilter(
        main_fk='activity',
        qs=RelatedActivity,
        lookup_expr='in',
        field_name='ref_activity__iati_identifier',
        fk='current_activity',)

    related_activity_type = ToManyFilter(
        main_fk='activity',
        qs=RelatedActivity,
        lookup_expr='in',
        field_name='type__code',
        fk='current_activity',)

    related_activity_recipient_country = ToManyFilter(
        main_fk='activity',
        qs=RelatedActivity,
        lookup_expr='in',
        field_name='ref_activity__recipient_country',
        fk='current_activity',)

    related_activity_recipient_region = ToManyFilter(
        main_fk='activity',
        qs=RelatedActivity,
        lookup_expr='in',
        field_name='ref_activity__recipient_region',
        fk='current_activity',)

    related_activity_sector = ToManyFilter(
        main_fk='activity',
        qs=RelatedActivity,
        lookup_expr='in',
        field_name='ref_activity__sector',
        fk='current_activity',)

    related_activity_sector_category = ToManyFilter(
        main_fk='activity',
        qs=RelatedActivity,
        lookup_expr='in',
        field_name='ref_activity__sector__category',
        fk='current_activity',)

    budget_currency = ToManyFilter(
        qs=Budget,
        lookup_expr='in',
        field_name='currency__code',
        fk='activity__budget',
    )

    recipient_country = ToManyFilter(
        qs=ActivityRecipientCountry,
        lookup_expr='in',
        field_name='country__code',
        fk='activity__budget',
    )

    recipient_region = ToManyFilter(
        qs=ActivityRecipientRegion,
        lookup_expr='in',
        field_name='region__code',
        fk='activity__budget',
    )

    recipient_region_not = ToManyFilter(
        qs=ActivityRecipientRegion,
        lookup_expr='in',
        field_name='region__code',
        fk='activity__budget',
    )

    sector = ToManyFilter(
        qs=ActivitySector,
        lookup_expr='in',
        field_name='sector__code',
        fk='activity__budget',
    )

    sector_startswith = ToManyFilter(
        main_fk='activity',
        qs=ActivitySector,
        lookup_expr='startswith',
        field_name='sector__code',
        fk='activity',
    )
    sector_vocabulary = ToManyFilter(
        qs=ActivitySector,
        lookup_expr='in',
        field_name='sector__vocabulary__code',
        fk='activity__budget',
    )

    sector_category = ToManyFilter(
        qs=ActivitySector,
        lookup_expr='in',
        field_name='sector__category__code',
        fk='activity__budget',
    )

    participating_organisation = ToManyFilter(
        qs=ActivityParticipatingOrganisation,
        lookup_expr='in',
        field_name='normalized_ref',
        fk='activity__budget',
    )

    participating_organisation_name = ToManyFilter(
        qs=ActivityParticipatingOrganisation,
        lookup_expr='in',
        field_name='primary_name',
        fk='activity__budget',
    )

    participating_organisation_role = ToManyFilter(
        qs=ActivityParticipatingOrganisation,
        lookup_expr='in',
        field_name='role__code',
        fk='activity__budget',
    )

    participating_organisation_type = ToManyFilter(
        qs=ActivityParticipatingOrganisation,
        lookup_expr='in',
        field_name='type__code',
        fk='activity__budget',
    )

    reporting_organisation_identifier = ToManyFilter(
        qs=ActivityReportingOrganisation,
        lookup_expr='in',
        field_name='organisation__organisation_identifier',
        fk='activity__budget',
    )

    reporting_organisation_identifier_startswith = ToManyFilter(
        qs=ActivityReportingOrganisation,
        lookup_expr='startswith',
        field_name='organisation__organisation_identifier',
        fk='activity__budget',
    )

    indicator_title = ToManyFilter(
        qs=ResultIndicatorTitle,
        lookup_expr='in',
        field_name='primary_name',
        fk='result_indicator__result__activity__budget')

    #
    # Transaction filters
    #

    transaction_type = ToManyFilter(
        qs=Transaction,
        lookup_expr='in',
        field_name='transaction_type',
        fk='activity__budget',
    )

    provider_organisation_primary_name = ToManyFilter(
        qs=Transaction,
        lookup_expr='in',
        field_name='provider_organisation__primary_name',
        fk='activity__budget',
    )

    receiver_organisation_primary_name = ToManyFilter(
        qs=Transaction,
        lookup_expr='in',
        field_name='receiver_organisation__primary_name',
        fk='activity__budget',
    )

    transaction_provider_organisation_name = ToManyFilter(
        qs=Transaction,
        lookup_expr='in',
        field_name='provider_organisation__narratives__content',
        fk='activity__budget',
    )

    transaction_receiver_organisation_name = ToManyFilter(
        qs=Transaction,
        lookup_expr='in',
        field_name='receiver_organisation__narratives__content',
        fk='activity__budget',
    )

    transaction_provider_activity = ToManyFilter(
        qs=Transaction,
        lookup_expr='in',
        field_name='provider_organisation__provider_activity_ref',
        fk='activity__budget',
    )

    transaction_currency = ToManyFilter(
        qs=Transaction,
        lookup_expr='in',
        field_name='currency',
        fk='activity__budget',
    )

    transaction_date_year = ToManyFilter(
        qs=Transaction,
        lookup_expr='year',
        field_name='transaction_date',
        fk='activity__budget'
    )

    #
    # Aggregated values filters
    #

    total_budget_lte = NumberFilter(
        lookup_expr='lte',
        field_name='activity__activity_aggregation__budget_value')

    total_budget_gte = NumberFilter(
        lookup_expr='gte',
        field_name='activity__activity_aggregation__budget_value')

    total_disbursement_lte = NumberFilter(
        lookup_expr='lte',
        field_name='activity__activity_aggregation__disbursement_value')

    total_disbursement_gte = NumberFilter(
        lookup_expr='gte',
        field_name='activity__activity_aggregation__disbursement_value')

    total_incoming_funds_lte = NumberFilter(
        lookup_expr='lte',
        field_name='activity__activity_aggregation__incoming_funds_value')

    total_incoming_funds_gte = NumberFilter(
        lookup_expr='gte',
        field_name='activity__activity_aggregation__incoming_funds_value')

    total_expenditure_lte = NumberFilter(
        lookup_expr='lte',
        field_name='activity__activity_aggregation__expenditure_value')

    total_expenditure_gte = NumberFilter(
        lookup_expr='gte',
        field_name='activity__activity_aggregation__expenditure_value')

    total_commitment_lte = NumberFilter(
        lookup_expr='lte',
        field_name='activity__activity_aggregation__commitment_value')

    total_commitment_gte = NumberFilter(
        lookup_expr='gte',
        field_name='activity__activity_aggregation__commitment_value')

    total_hierarchy_budget_lte = NumberFilter(
        lookup_expr='lte',
        field_name='activity__activity_plus_child_aggregation__budget_value')

    total_hierarchy_budget_gte = NumberFilter(
        lookup_expr='gte',
        field_name='activity__activity_plus_child_aggregation__budget_value')

    total_hierarchy_disbursement_lte = NumberFilter(
        lookup_expr='lte',
        field_name='activity__activity_plus_child_aggregation__disbursement_value')  # NOQA: E501

    total_hierarchy_disbursement_gte = NumberFilter(
        lookup_expr='gte',
        field_name='activity__activity_plus_child_aggregation__disbursement_value')  # NOQA: E501

    total_hierarchy_incoming_funds_lte = NumberFilter(
        lookup_expr='lte',
        field_name='activity__activity_plus_child_aggregation__incoming_funds_value')  # NOQA: E501

    total_hierarchy_incoming_funds_gte = NumberFilter(
        lookup_expr='gte',
        field_name='activity__activity_plus_child_aggregation__incoming_funds_value')  # NOQA: E501

    total_hierarchy_expenditure_lte = NumberFilter(
        lookup_expr='lte',
        field_name='activity__activity_plus_child_aggregation__expenditure_value')  # NOQA: E501

    total_hierarchy_expenditure_gte = NumberFilter(
        lookup_expr='gte',
        field_name='activity__activity_plus_child_aggregation__expenditure_value')  # NOQA: E501

    total_hierarchy_commitment_lte = NumberFilter(
        lookup_expr='lte',
        field_name='activity__activity_plus_child_aggregation__commitment_value')  # NOQA: E501

    total_hierarchy_commitment_gte = NumberFilter(
        lookup_expr='gte',
        field_name='activity__activity_plus_child_aggregation__commitment_value')  # NOQA: E501

    class Meta:
        model = Budget
        fields = '__all__'


class RelatedOrderingFilter(filters.OrderingFilter):
    """
    Extends OrderingFilter to support ordering by fields in related models
    using the Django ORM __ notation

    Also provides support for mapping of fields,
    in remove_invalid_fields a mapping is maintained
    to make 'user-friendly' names possible
    """

    def get_ordering(self, request, queryset, view):
        ordering = super(RelatedOrderingFilter, self).get_ordering(
            request, queryset, view)

        always_ordering = getattr(view, 'always_ordering', None)

        if ordering and always_ordering:
            ordering = ordering + [always_ordering]
            queryset.distinct(always_ordering)

        return ordering

    def filter_queryset(self, request, queryset, view):

        ordering = self.get_ordering(request, queryset, view)

        if ordering:
            ordering = [order.replace("-", "") for order in ordering]

            if 'iati_identifier' not in ordering:
                queryset = queryset.distinct(*ordering)

        return super(RelatedOrderingFilter, self).filter_queryset(
            request, queryset, view)

    def is_valid_field(self, model, field):
        """
        Return true if the field exists within the model (or in the related
        model specified using the Django ORM __ notation)
        """
        components = field.split('__', 1)
        try:
            field = model._meta.get_field(components[0])

            if isinstance(field, OneToOneRel):
                return self.is_valid_field(field.related_model, components[1])

            # reverse relation
            if isinstance(field, ForeignObjectRel):
                return self.is_valid_field(field.model, components[1])

            # foreign key
            if field.remote_field and len(components) == 2:
                return self.is_valid_field(
                    field.remote_field.model, components[1]
                )
            return True
        except FieldDoesNotExist:
            return False
