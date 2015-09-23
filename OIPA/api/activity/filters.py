from iati.models import Activity, Budget, RelatedActivity
from django_filters import Filter, FilterSet, NumberFilter, DateFilter
from api.generics.filters import CommaSeparatedCharFilter

class CommaSeparatedDateRangeFilter(Filter):

    def filter(self, qs, value):

        if value in ([], (), {}, None, ''):
            return qs

        value = value.split(',')

        if len(value) is 2:
            lte = value[0]
            gte = value[0]

        return super(CommaSeparatedCharFilter, self).filter(qs, value)


class TogetherFilter(Filter):
    """
    Used with TogetherFilterSet, always gets called regardless of GET args
    """
    
    def __init__(self, filters=None, values=None, **kwargs):
        self.filter_classes = filters
        self.values = values

        super(TogetherFilter, self).__init__(**kwargs)

    def filter(self, qs, values):
        if self.filter_classes:
            filters = { "%s__%s" % (c[0].name, c[0].lookup_type) : c[1] for c in zip(self.filter_classes, values)}
            qs = qs.filter(**filters).distinct()

            return qs

import uuid

class TogetherFilterSet(FilterSet):
    def __init__(self, data=None, queryset=None, prefix=None, strict=None):
        """
        Adds a together_exclusive meta option that selects fields that have to 
        be called in the same django filter() call when both present
        """

        meta = getattr(self, 'Meta', None)

        # fields that must be filtered in the same filter call
        self.together_exclusive = getattr(meta, 'together_exclusive', None)

        data = data.copy()

        for filterlist in self.together_exclusive:
            if set(filterlist).issubset(data.keys()):

                filter_values = [ data.pop(filteritem)[0] for filteritem in filterlist ]
                filter_classes = [ self.declared_filters.get(filteritem, None) for filteritem in filterlist ]

                uid = uuid.uuid4()

                self.base_filters[uid] = TogetherFilter(filters=filter_classes)
                data.appendlist(uid, filter_values)

        super(FilterSet, self).__init__(data, queryset, prefix, strict)


class ActivityFilter(TogetherFilterSet):

    ids = CommaSeparatedCharFilter(
        name='id',
        lookup_type='in')

    activity_scope = CommaSeparatedCharFilter(
        name='scope__code',
        lookup_type='in')

    recipient_country = CommaSeparatedCharFilter(
        lookup_type='in',
        name='recipient_country'
    )

    recipient_region = CommaSeparatedCharFilter(
        lookup_type='in',
        name='recipient_region')

    start_date_actual_lte = DateFilter(
        lookup_type='lte',
        name='start_actual')

    start_date_actual_gte = DateFilter(
        lookup_type='gte',
        name='start_actual')

    sector = CommaSeparatedCharFilter(
        lookup_type='in',
        name='sector')
    sector_category = CommaSeparatedCharFilter(
        lookup_type='in',
        name='activitysector__sector__category__code')

    participating_organisation = CommaSeparatedCharFilter(
        lookup_type='in',
        name='participating_organisation'
    )
    reporting_organisation = CommaSeparatedCharFilter(
        lookup_type='in',
        name='reporting_organisation'
    )

    xml_source_ref = CommaSeparatedCharFilter(
        lookup_type='in',
        name='xml_source_ref'
    )

    activity_status = CommaSeparatedCharFilter(
        lookup_type='in',
        name='activity_status',
        distinct=True)

    hierarchy = CommaSeparatedCharFilter(
        lookup_type='in',
        name='hierarchy')

    related_activity_id = CommaSeparatedCharFilter(
        lookup_type='in',
        name='current_activity__related_activity__id', distinct=True)

    related_activity_type = CommaSeparatedCharFilter(
        lookup_type='in',
        name='current_activity__type__code',
        distinct=True)

    related_activity_recipient_country = CommaSeparatedCharFilter(
        lookup_type='in',
        name='current_activity__related_activity__recipient_country',
        distinct=True)

    related_activity_recipient_region = CommaSeparatedCharFilter(
        lookup_type='in',
        name='current_activity__related_activity__recipient_region',
        distinct=True)

    related_activity_sector = CommaSeparatedCharFilter(
        lookup_type='in',
        name='current_activity__related_activity__sector',
        distinct=True)

    related_activity_sector_category = CommaSeparatedCharFilter(
        lookup_type='in',
        name='current_activity__related_activity__sector__category',
        distinct=True)

    budget_period_start = DateFilter(
        lookup_type='gte',
        name='budget__period_start')

    budget_period_end = DateFilter(
        lookup_type='lte',
        name='budget__period_end')

    # Deprecated
    min_total_budget = NumberFilter(
        lookup_type='gte',
        name='total_budget')

    max_total_budget = NumberFilter(
        lookup_type='lte',
        name='total_budget')

    transaction_provider_activity = CommaSeparatedCharFilter(
        lookup_type='in',
        name='transaction__provider_activity', distinct=True)

    class Meta:
        model = Activity
        together_exclusive = [('budget_period_start', 'budget_period_end')]

class BudgetFilter(FilterSet):

    budget_period_start = DateFilter(
        lookup_type='gte',
        name='period_start')

    budget_period_end = DateFilter(
        lookup_type='lte',
        name='period_end')

    class Meta:
        model = Budget

class RelatedActivityFilter(FilterSet):

    related_activity_type = CommaSeparatedCharFilter(
        lookup_type='in',
        name='type__code')

    class Meta:
        model = RelatedActivity


 
