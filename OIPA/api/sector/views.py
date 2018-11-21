
from rest_framework.generics import RetrieveAPIView
from rest_framework_extensions.cache.mixins import CacheResponseMixin

import iati
from api.cache import QueryParamsKeyConstructor
from api.generics.views import DynamicListView
from api.sector import serializers


class SectorList(CacheResponseMixin, DynamicListView):
    """
    Returns a list of IATI Sectors stored in OIPA.

    ## Request parameters

    - `fields` (*optional*): List of fields to display
    - `fields[aggregations]` (*optional*): Aggregate available information.
        See [Available aggregations]() section for details.

    ## Result details

    Each result item contains short information about sector
    including URI to sector details.

    URI is constructed as follows: `/api/sectors/{sector_id}`

    """

    queryset = iati.models.Sector.objects.all()
    serializer_class = serializers.SectorSerializer
    fields = ('url', 'code', 'name')
    list_cache_key_func = QueryParamsKeyConstructor()


class SectorDetail(CacheResponseMixin, RetrieveAPIView):
    """
    Returns detailed information about Sector.

    ## URI Format

    ```
    /api/sectors/{sector_id}
    ```

    ### URI Parameters

    - `sector_id`: Numerical ID of desired Sector

    ## Request parameters

    - `fields` (*optional*): List of fields to display

    """
    queryset = iati.models.Sector.objects.all()
    serializer_class = serializers.SectorSerializer
