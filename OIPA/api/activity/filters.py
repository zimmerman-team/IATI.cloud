from iati.models import Activity, Budget, RelatedActivity
from django_filters import Filter, FilterSet, NumberFilter, CharFilter, ChoiceFilter, DateFilter

class CommaSeparatedCharFilter(CharFilter):

    def filter(self, qs, value):

        if value:
            value = value.split(',')

        return super(CommaSeparatedCharFilter, self).filter(qs, value)

class ActivityFilter(FilterSet):

    ids = CommaSeparatedCharFilter(name='id', lookup_type='in')

    activity_scope = CommaSeparatedCharFilter(name='scope__code', lookup_type='in')

    recipient_country = CommaSeparatedCharFilter(
        lookup_type='in',
        name='recipient_country'
    )

    recipient_region = CommaSeparatedCharFilter(lookup_type='in', name='recipient_region')

    sector = CommaSeparatedCharFilter(lookup_type='in', name='sector')
    sector_category = CommaSeparatedCharFilter(lookup_type='in', name='activitysector__sector__category__code')

    participating_organisation = CommaSeparatedCharFilter(
        lookup_type='in',
        name='participating_organisation'
    )
    reporting_organisation = CommaSeparatedCharFilter(
        lookup_type='in',
        name='reporting_organisation'
    )

    # hierarchy = ChoiceFilter(choices=Activity.hierarchy_choices, name='hierarchy')
    hierarchy = CommaSeparatedCharFilter(lookup_type='in', name='hierarchy')
    
    # Nescessary for removing activities which fail these filters
    related_activity_id = CommaSeparatedCharFilter(lookup_type='in', name='current_activity__current_activity__id')
    related_activity_type = CommaSeparatedCharFilter(lookup_type='in', name='current_activity__type__code')
    related_activity_recipient_country = CommaSeparatedCharFilter(lookup_type='in', name='current_activity__current_activity__recipient_country')
    related_activity_recipient_region = CommaSeparatedCharFilter(lookup_type='in', name='current_activity__current_activity__recipient_region')
    related_activity_sector = CommaSeparatedCharFilter(lookup_type='in', name='current_activity__current_activity__sector')

    budget_period_start = DateFilter(lookup_type='gte', name='budget__period_start')
    budget_period_end = DateFilter(lookup_type='lte', name='budget__period_end')

    # Deprecated
    min_total_budget = NumberFilter(lookup_type='gte', name='total_budget')
    max_total_budget = NumberFilter(lookup_type='lte', name='total_budget')

    class Meta:
        model = Activity

class BudgetFilter(FilterSet):

    budget_period_start = DateFilter(lookup_type='gte', name='period_start')
    budget_period_end = DateFilter(lookup_type='lte', name='period_end')

    class Meta:
        model = Budget

class RelatedActivityFilter(FilterSet):

    related_activity_type = CommaSeparatedCharFilter(lookup_type='in', name='type__code')

    class Meta:
        model = RelatedActivity


 
