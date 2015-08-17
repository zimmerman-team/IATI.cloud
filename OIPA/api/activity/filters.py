from iati.models import Activity
from django_filters import Filter, FilterSet, NumberFilter, CharFilter, ChoiceFilter

class CommaSeparatedCharFilter(CharFilter):

    def filter(self, qs, value):

        if value:
            value = value.split(',')

        return super(CommaSeparatedCharFilter, self).filter(qs, value)

class ActivityFilter(FilterSet):

    ids = CommaSeparatedCharFilter(name='id', lookup_type='in')

    activity_scope = CommaSeparatedCharFilter(name='scope__code', lookup_type='in')

    recipient_countries = CommaSeparatedCharFilter(
        lookup_type='in',
        name='recipient_country'
    )

    recipient_regions = CommaSeparatedCharFilter(lookup_type='in', name='recipient_region')
    sectors = CommaSeparatedCharFilter(lookup_type='in', name='sector')

    participating_organisations = CommaSeparatedCharFilter(
        lookup_type='in',
        name='participating_organisation'
    )
    reporting_organisations = CommaSeparatedCharFilter(
        lookup_type='in',
        name='reporting_organisation'
    )
    
    min_total_budget = NumberFilter(lookup_type='gte', name='total_budget')
    max_total_budget = NumberFilter(lookup_type='lte', name='total_budget')

    hierarchy = ChoiceFilter(choices=Activity.hierarchy_choices, name='hierarchy')
    related_activity_type = CommaSeparatedCharFilter(lookup_type='in', name='current_activity__type__code')



    class Meta:
        model = Activity
        names = [
            'activity_scope',
            'reporting_organisations',
            'recipient_countries',
            'recipient_regions',
            'sectors',
            'participating_organisations',
            'min_total_budget',
            'max_total_budget',
            'hierarchy',
        ]
