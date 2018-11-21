from api.generics.filters import CommaSeparatedCharFilter, TogetherFilterSet
from iati.models import Location


class LocationFilter(TogetherFilterSet):

    activity_status = CommaSeparatedCharFilter(
        lookup_expr='in',
        field_name='activity__activity_status',)

    class Meta:
        model = Location
        fields = ['activity_status']
