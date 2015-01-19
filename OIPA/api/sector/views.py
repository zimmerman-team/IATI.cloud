import iati
from rest_framework import generics
from api.sector import serializers
from api.activity.views import ActivityList
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView


class SectorList(ListAPIView):
    """
    Returns a list of IATI Sectors stored in OIPA.

    ## Request parameters

    - `fields` (*optional*): List of fields to display
    - `fields[aggregations]` (*optional*): Aggregate available information.
        See [Available aggregations]() section for details.

    ## Available aggregations

    API request may include `fields[aggregations]` parameter.
    This parameter controls result aggregations and
    can be one or more (comma separated values) of:

    - `total_budget`: Calculate total budget of activities
        presented in sector activities list.
    - `disbursement`: Calculate total disbursement of activities
        presented in sector activities list.
    - `commitment`: Calculate total commitment of activities
        presented in sector activities list.

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


class SectorActivities(ActivityList):
    """
    Returns a list of IATI Activities within sector.

    ## URI Format

    ```
    /api/sectors/{sector_id}/activities
    ```

    ### URI Parameters

    - `sector_id`: Desired sector ID

    """
    def get_queryset(self):
        pk = self.kwargs.get('pk')
        sector = iati.models.Sector.objects.get(pk=pk)
        return sector.activity_set.all()
