from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from iati.models import Location

from api.generics.views import DynamicListView
from api.location.serializers import LocationSerializer
from api.location.filters import LocationFilter
from api.generics.filters import DistanceFilter


class LocationList(DynamicListView):
    """
    Returns a list of IATI locations stored in OIPA.

    ## Request parameters
    - `activity_id` (*optional*): Comma separated list of activity id's.

    """

    queryset = Location.objects.all().order_by('id')
    filter_backends = (DjangoFilterBackend, DistanceFilter)
    filter_class = LocationFilter
    serializer_class = LocationSerializer

    fields = (
        'id',
        'url',
        'activity',
        'ref',
        'location_reach',
        'location_id',
        'name',
        'description',
        'activity_description',
        'administrative',
        'point',
        'exactness',
        'location_class',
        'feature_designation',
    )

    always_ordering = 'id'

    ordering_fields = ()


class LocationDetail(RetrieveAPIView):
    """
    Returns detailed information about a Location.

    ## URI Format

    ```
    /api/locations/{location_id}
    ```

    ### URI Parameters

    - `location_id`: Desired location ID

    """
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
