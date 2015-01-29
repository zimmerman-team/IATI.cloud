from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from geodata.models import City
from api.city import serializers
from api.indicator.views import IndicatorList


class CityList(ListAPIView):
    """
    Returns a list of IATI Cities stored in OIPA.

    ## Request parameters

    - `fields` (*optional*): List of fields to display
    - `fields[aggregations]` (*optional*): Aggregate available information.
        See [Available aggregations]() section for details.

    ## Available aggregations

    API request may include `fields[aggregations]` parameter.
    This parameter controls result aggregations and
    can be one or more (comma separated values) of:

    - `total_budget`: Calculate total budget of activities
        presented in cities activities list.
    - `disbursement`: Calculate total disbursement of activities
        presented in cities activities list.
    - `commitment`: Calculate total commitment of activities
        presented in cities activities list.

    ## Result details

    Each result item contains short information about city including URI
    to city details.

    URI is constructed as follows: `/api/cities/{city_id}`

    """
    queryset = City.objects.all()
    serializer_class = serializers.CitySerializer
    fields = ('url', 'id', 'name')


class CityDetail(RetrieveAPIView):
    """
    Returns detailed information about City.

    ## URI Format

    ```
    /api/cities/{city_id}
    ```

    ### URI Parameters

    - `city_id`: Numerical ID of desired City

    ## Request parameters

    - `fields` (*optional*): List of fields to display

    ## Extra Endpoints

    ### City Indicators

    `/api/cities/{city_id}/indicators`: List of indicators
    connected to specified city.

    """
    queryset = City.objects.all()
    serializer_class = serializers.CitySerializer


class CityIndicators(IndicatorList):
    """
    Returns a list of IATI City indicators stored in OIPA.

    ## URI Format

    ```
    /api/cities/{city_id}/indicators
    ```

    ### URI Parameters

    - `city_id`: Numerical ID of desired City

    ## Result details

    Each result item contains short information about indicator including URI
    to indicator details.

    URI is constructed as follows: `/api/indicators/{indicator_id}`

    """
    def get_queryset(self):
        pk = self.kwargs.get('pk')
        city = City.objects.get(pk=pk)
        return city.indicatordata_set.all()
