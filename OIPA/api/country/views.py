import geodata
from api.country import serializers
from geodata.models import Country
from rest_framework.generics import RetrieveAPIView
from api.country.filters import CountryFilter
from api.generics.views import DynamicListView
from rest_framework_extensions.cache.mixins import CacheResponseMixin


class CountryList(CacheResponseMixin, DynamicListView):
    """
    Returns a list of IATI Countries stored in OIPA.

    ## Request parameters

    - `code` (*optional*): Country code to search for.
    - `name` (*optional*): Country name to search for.
    - `region_code` (*optional*): Filter countries by Region code.
    - `fields` (*optional*): List of fields to display.
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
    queryset = geodata.models.Country.objects.all().order_by('code')
    serializer_class = serializers.CountrySerializer
    filter_class = CountryFilter

    fields = ('url', 'code', 'name',)


class CountryDetail(CacheResponseMixin, RetrieveAPIView):
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
