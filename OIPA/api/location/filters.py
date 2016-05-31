from api.generics.filters import TogetherFilterSet
from iati.models import Location
from api.generics.filters import CommaSeparatedCharFilter


class LocationFilter(TogetherFilterSet):

    activity_status = CommaSeparatedCharFilter(
        lookup_type='in',
        name='activity__activity_status',)

    class Meta:
        model = Location

