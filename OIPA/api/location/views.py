from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework.generics import RetrieveAPIView
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from api.activity.serializers import LocationSerializer
from api.generics.filters import DistanceFilter
from api.generics.views import DynamicDetailView, DynamicListView
from api.location.filters import LocationFilter, RelatedOrderingFilter
from iati.models import Location


class LocationList(CacheResponseMixin, DynamicListView):
    """
    Returns a list of IATI locations stored in OIPA.

    ## Request parameters
    - `activity_id` (*optional*): Comma separated list of activity id's.

    """

    queryset = Location.objects.all().order_by('id')
    filter_backends = (DjangoFilterBackend, DistanceFilter, RelatedOrderingFilter)  # NOQA: E501
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
    # exceptional_fields = []  # NOQA: E501

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
            'iati_identifier': {'header': 'activity_id'},
            'sectors.sector.code': {'header': 'sector_code'},
            'sectors.percentage': {'header': 'sectors_percentage'},
            'recipient_countries.country.code': {'header': 'country'},
            'recipient_regions.region.code': {'header': 'region'},
            # 'locations': {'header': 'locations'},
            # 'location_reach.code': {'header': 'location_reach'},
            # 'location_id.code': {'header': None},
            # 'administrative.code': {'header': None},
            # 'exactness.code': {'header': None},
            # 'point.pos.latitude': {'header': None},
            # 'point.pos.longitude': {'header': None},
            # 'location_class.code': {'header': None},
            # 'feature_designation.code': {'header': None},
            # 'ref': {'header': None},
            # 'descriptions.narratives.text': {'header': None},
            # 'title.narratives.text': {'header': None},
            # 'activity_description.narratives.text': {'header': None},
            # 'name.narratives.text': {'header': None},
        }

    always_ordering = 'id'

    ordering_fields = ()


class LocationDetail(CacheResponseMixin, DynamicDetailView):
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
    filter_backends = (DjangoFilterBackend, DistanceFilter, RelatedOrderingFilter)  # NOQA: E501
    filter_class = LocationFilter

    selectable_fields = ()

    # for transaction_type in list(TransactionType.objects.all()):
    #    transaction_types.append(transaction_type.code)

    # Activity break down column
    break_down_by = 'sectors'
    # selectable fields which required different render logic.
    # Instead merging values using the delimiter, this fields will generate
    # additional columns for the different values, based on defined criteria.
    exceptional_fields = [{'locations': []}]  # NOQA: E501
    # exceptional_fields = []  # NOQA: E501

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
            'iati_identifier': {'header': 'activity_id'},
            'sectors.sector.code': {'header': 'sector_code'},
            'sectors.percentage': {'header': 'sectors_percentage'},
            'recipient_countries.country.code': {'header': 'country'},
            'recipient_regions.region.code': {'header': 'region'},
        }
