import iati
from rest_framework import generics
from api.sector import serializers
from api.activity.views import ActivityList
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView

from api.generics.views import DynamicListView, DynamicDetailView


class SectorList(DynamicListView):
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


class SectorDetail(RetrieveAPIView):
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

