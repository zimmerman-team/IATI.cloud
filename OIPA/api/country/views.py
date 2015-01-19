import geodata
from api.country import serializers
from api.activity.views import ActivityList
from api.city.serializers import CitySerializer
from api.indicator.serializers import IndicatorSerializer
from geodata.models import Country
from indicator.models import IndicatorData
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView


class CountryList(ListAPIView):
    """
    Returns a list of IATI Countries stored in OIPA.

    ## Request parameters

    - `fields` (*optional*): List of fields to display
    - `fields[aggregations]` (*optional*): Aggregate available information.
        See [Available aggregations]() section for details.

    ## Available aggregations

    API request may include `fields[aggregations]` parameter.
    This parameter controls result aggregations and
    can be one or more (comma separated values) of:

    - `total_budget`: Calculate total budget of activities
        presented in countries activities list.
    - `disbursement`: Calculate total disbursement of activities
        presented in countries activities list.
    - `commitment`: Calculate total commitment of activities
        presented in countries activities list.

    ## Result details

    Each result item contains short information about country including URI
    to country details.

    URI is constructed as follows: `/api/counties/{country_id}`

    """
    queryset = geodata.models.Country.objects.all()
    serializer_class = serializers.CountrySerializer
    fields = ('url', 'code', 'name')


class CountryDetail(RetrieveAPIView):
    """
    Returns detailed information about Country.

    ## URI Format

    ```
    /api/countries/{country_id}
    ```

    ### URI Parameters

    - `country_id`: Numerical ID of desired Country

    ## Request parameters

    - `fields` (*optional*): List of fields to display

    """
    queryset = geodata.models.Country.objects.all()
    serializer_class = serializers.CountrySerializer


class CountryActivities(ActivityList):
    """
    Returns a list of IATI Activities connected to Country stored in OIPA.

    ## URI Format

    ```
    /api/countries/{country_id}/activities
    ```

    ### URI Parameters

    - `country_id`: Numerical ID of desired Country

    ## Result details

    Each result item contains short information about activity including URI
    to activity details.

    URI is constructed as follows: `/api/activities/{activity_id}`

    """
    def get_queryset(self):
        pk = self.kwargs.get('pk')
        country = Country.objects.get(pk=pk)
        return country.activity_set.all()


class CountryIndicators(ListAPIView):
    """
    Returns a list of IATI Country indicators stored in OIPA.

    ## URI Format

    ```
    /api/countries/{country_id}/indicators
    ```

    ### URI Parameters

    - `country_id`: Numerical ID of desired Country

    ## Result details

    Each result item contains short information about indicator including URI
    to indicator details.

    URI is constructed as follows: `/api/indicators/{city_id}`

    """

    queryset = IndicatorData.objects.all()
    serializer_class = IndicatorSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        country = Country.objects.get(pk=pk)
        return country.indicatordata_set.all()


class CountryCities(ListAPIView):
    """
    Returns a list of IATI Country cities stored in OIPA.

    ## URI Format

    ```
    /api/countries/{country_id}/cities
    ```

    ### URI Parameters

    - `country_id`: Numerical ID of desired Country

    ## Result details

    Each result item contains short information about city including URI
    to city details.

    URI is constructed as follows: `/api/cities/{city_id}`

    """
    queryset = IndicatorData.objects.all()
    serializer_class = CitySerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        country = Country.objects.get(pk=pk)
        return country.city_set.all()
