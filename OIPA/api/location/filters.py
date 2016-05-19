from api.generics.filters import TogetherFilterSet
from iati.models import Location


class LocationFilter(TogetherFilterSet):


    class Meta:
        model = Location

