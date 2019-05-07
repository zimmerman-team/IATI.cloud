from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import RetrieveAPIView
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from api.activity.serializers import LocationSerializer
from api.generics.filters import DistanceFilter
from api.generics.views import DynamicListView
from api.location.filters import LocationFilter, RelatedOrderingFilter
from iati.models import Location


class LocationList(CacheResponseMixin, DynamicListView):
    """
    Returns a list of IATI locations stored in OIPA.

    ## Request parameters
    - `activity_id` (*optional*): Comma separated list of activity id's.

    """

    queryset = Location.objects.all().order_by('id')
    filter_backends = (DjangoFilterBackend, DistanceFilter, RelatedOrderingFilter)
    filter_class = LocationFilter
    serializer_class = LocationSerializer

    selectable_fields = ()
    # Get all transaction type
    transaction_types = []
    # for transaction_type in list(TransactionType.objects.all()):
    #    transaction_types.append(transaction_type.code)

    # Activity break down column
    break_down_by = 'sectors'
    # selectable fields which required different render logic.
    # Instead merging values using the delimiter, this fields will generate
    # additional columns for the different values, based on defined criteria.
    exceptional_fields = [{'locations': transaction_types}]  # NOQA: E501

    fields = (
        'iati_identifier',
        'sectors',
        'recipient_regions',
        'recipient_countries',
        'locations'

    )
    # column headers with paths to the json property value.
    # reference to the field name made by the first term in the path
    # example: for recipient_countries.country.code path
    # reference field name is first term, meaning recipient_countries.
    csv_headers = \
        {
            'activity_id': 'iati_identifier',
            'sector_code': 'sectors.sector.code',
            'sectors_percentage': 'sectors.percentage',
            'country': 'recipient_countries.country.code',
            'region': 'recipient_regions.region.code',
            'locations': 'locations'
        }

    path_value = \
        {
             'location_reach.code',
             'location_id.code',
             'administrative.code',
             'exactness.code',
             'point.pos.latitude',
             'point.pos.longitude',
             'location_class.code',
             'feature_designation.code',
             'ref',
             'descriptions.narratives.text',
             'title.narratives.text',
             'activity_description.narratives.text',
             'name.narratives.text'
        }
    ''' 
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
    '''
    always_ordering = 'id'

    ordering_fields = ()


class LocationDetail(CacheResponseMixin, RetrieveAPIView):
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
