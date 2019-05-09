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
            'iati_identifier': {'header': 'activity_id', 'field_name':'iati_identifier'},
            'sectors.sector.code': {'header': 'sector_code', 'field_name':'iati_identifier'},
            'sectors.percentage': {'header': 'sectors_percentage', 'field_name':'iati_identifier'},
            'recipient_countries.country.code': {'header': 'country', 'field_name':'iati_identifier'},
            'recipient_regions.region.code': {'header': 'region', 'field_name':'iati_identifier'},
            'locations': {'header': 'locations', 'field_name':'iati_identifier'},
            'locations.location_reach.code': {'header': None, 'field_name':'iati_identifier'},
            'location_id.code': {'header': None, 'field_name':'iati_identifier'},
            'administrative.code': {'header': None, 'field_name':'iati_identifier'},
            'exactness.code': {'header': None, 'field_name': 'exactness'},
            'point.pos.latitude': {'header': None, 'field_name': 'point'},
            'point.pos.longitude': {'header': None, 'field_name': 'point'},
            'location_class.code': {'header': None, 'field_name':' location_class'},
            'feature_designation.code': {'header': None, 'field_name':'feature_designation'},
            'ref': {'header': None, 'field_name': 'ref'},
            'descriptions.narratives.text': {'header': None, 'field_name': 'descriptions'},
            'title.narratives.text': {'header': None, 'field_name':'title'},
            'activity_description.narratives.text': {'header': None, 'field_name':'activity_description'},
            'name.narratives.text': {'header': None, 'field_name':'name'},
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
