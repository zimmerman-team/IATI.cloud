import geodata
from api.region import serializers
from rest_framework.generics import RetrieveAPIView

from api.generics.views import DynamicListView, DynamicDetailView

class RegionList(DynamicListView):
    """
    Returns a list of IATI Regions stored in OIPA.

    ## Request parameters

    - `fields` (*optional*): List of fields to display
    - `fields[aggregations]` (*optional*): Aggregate available information.
        See [Available aggregations]() section for details.

    ## Available aggregations

    API request may include `fields[aggregations]` parameter.
    This parameter controls result aggregations and
    can be one or more (comma separated values) of:

    - `total_budget`: Calculate total budget of activities
        presented in regions activities list.
    - `disbursement`: Calculate total disbursement of activities
        presented in regions activities list.
    - `commitment`: Calculate total commitment of activities
        presented in regions activities list.

    ## Result details

    Each result item contains short information about region
    including URI to region details.

    URI is constructed as follows: `/api/regions/{region_id}`

    """
    queryset = geodata.models.Region.objects.all()
    serializer_class = serializers.RegionSerializer
    fields = ('url', 'code', 'name')


class RegionDetail(RetrieveAPIView):
    """
    Returns detailed information about Region.

    ## URI Format

    ```
    /api/regions/{region_id}
    ```

    ### URI Parameters

    - `region_id`: Numerical ID of desired Region

    ## Request parameters

    - `fields` (*optional*): List of fields to display

    """
    queryset = geodata.models.Region.objects.all()
    serializer_class = serializers.RegionSerializer

