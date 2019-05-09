from django_filters import BooleanFilter, DateFilter, NumberFilter

from api.generics.filters import (
    CommaSeparatedCharFilter, CommaSeparatedStickyCharFilter,
    StickyBooleanFilter, StickyCharFilter, TogetherFilterSet, ToManyFilter
)
from iati.models import (
    ActivityParticipatingOrganisation, ActivityRecipientCountry,
    ActivityRecipientRegion, ActivityReportingOrganisation, ActivitySector,
    DocumentLink, RelatedActivity, Result
)

from rest_framework import filters
from django.db.models.fields.related import ForeignObjectRel, OneToOneRel
from django.db.models.fields import FieldDoesNotExist


class ResultFilter(TogetherFilterSet):

    activity_id = CommaSeparatedCharFilter(
        field_name='activity__iati_identifier',
        lookup_expr='in')

    result_title = CommaSeparatedStickyCharFilter(
        field_name='resulttitle__primary_name',
        lookup_expr='in',
    )

    indicator_title = CommaSeparatedStickyCharFilter(
        field_name='resultindicator__resultindicatortitle__primary_name',
        lookup_expr='in',
    )

    indicator_period_actual_null = StickyBooleanFilter(
        lookup_expr='isnull',
        field_name='resultindicator__resultindicatorperiod__actual')

    result_indicator_period_end_year = StickyCharFilter(
        field_name='resultindicator__resultindicatorperiod__period_end',
        lookup_expr='year'
    )

    # default filters
    activity_scope = CommaSeparatedCharFilter(
        field_name='activity__scope__code',
        lookup_expr='in',)

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

    end_date_isnull = BooleanFilter(field_name='activity__end_date__isnull')
    start_date_isnull = BooleanFilter(
        field_name='activity__start_date__isnull'
    )

    activity_status = CommaSeparatedCharFilter(
        lookup_expr='in',
        field_name='activity__activity_status',)

    document_link_category = ToManyFilter(
        main_fk='activity',
        qs=DocumentLink,
        fk='activity',
        lookup_expr='in',
        field_name='categories__code',
    )

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
        field_name='activity__budget__period_start',)

    budget_period_end = DateFilter(
        lookup_expr='lte',
        field_name='activity__budget__period_end')

    recipient_country = ToManyFilter(
        main_fk='activity',
        qs=ActivityRecipientCountry,
        lookup_expr='in',
        field_name='country__code',
        fk='activity',
    )

    recipient_region = ToManyFilter(
        main_fk='activity',
        qs=ActivityRecipientRegion,
        lookup_expr='in',
        field_name='region__code',
        fk='activity',
    )

    sector = ToManyFilter(
        main_fk='activity',
        qs=ActivitySector,
        lookup_expr='in',
        field_name='sector__code',
        fk='activity',
    )

    sector_vocabulary = ToManyFilter(
        main_fk='activity',
        qs=ActivitySector,
        lookup_expr='in',
        field_name='sector__vocabulary__code',
        fk='activity',
    )

    sector_category = ToManyFilter(
        main_fk='activity',
        qs=ActivitySector,
        lookup_expr='in',
        field_name='sector__category__code',
        fk='activity',
    )

    participating_organisation = ToManyFilter(
        main_fk='activity',
        qs=ActivityParticipatingOrganisation,
        lookup_expr='in',
        field_name='normalized_ref',
        fk='activity',
    )

    participating_organisation_name = ToManyFilter(
        main_fk='activity',
        qs=ActivityParticipatingOrganisation,
        lookup_expr='in',
        field_name='primary_name',
        fk='activity',
    )

    participating_organisation_role = ToManyFilter(
        main_fk='activity',
        qs=ActivityParticipatingOrganisation,
        lookup_expr='in',
        field_name='role__code',
        fk='activity',
    )

    participating_organisation_type = ToManyFilter(
        main_fk='activity',
        qs=ActivityParticipatingOrganisation,
        lookup_expr='in',
        field_name='type__code',
        fk='activity',
    )

    reporting_organisation_identifier = ToManyFilter(
        main_fk='activity',
        qs=ActivityReportingOrganisation,
        lookup_expr='in',
        field_name='organisation__organisation_identifier',
        fk='activity',
    )

    related_activity_id = ToManyFilter(
        main_fk='activity',
        qs=RelatedActivity,
        fk='current_activity',
        lookup_expr='in',
        field_name='ref_activity__iati_identifier',
    )

    total_incoming_funds_lte = NumberFilter(
        lookup_expr='lte',
        field_name='activity__activity_aggregation__incoming_funds_value')

    total_incoming_funds_gte = NumberFilter(
        lookup_expr='gte',
        field_name='activity__activity_aggregation__incoming_funds_value')

    class Meta:
        model = Result
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