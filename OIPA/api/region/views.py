import geodata
from iati.models import Activity
from api.region import serializers
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from api.country.serializers import CountrySerializer
from api.activity.views import ActivityList


class RegionList(ListAPIView):
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


class RegionCountries(ListAPIView):
    """
    Returns a list of IATI Countries within region.

    ## URI Format

    ```
    /api/regions/{region_id}/countries
    ```

    ### URI Parameters

    - `region_id`: Desired region ID

    """
    serializer_class = CountrySerializer
    fields = ('url', 'code', 'name')

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        region = geodata.models.Region.objects.get(pk=pk)
        return region.countries


class RegionActivities(ActivityList):
    """
    Returns a list of IATI Activities within region.

    ## URI Format

    ```
    /api/regions/{region_id}/activities
    ```

    ### URI Parameters

    - `region_id`: Desired region ID

    """
    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Activity.objects.in_region(pk)
