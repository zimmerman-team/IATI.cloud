from api import generics
import iati
from api.sector import serializers


class SectorList(generics.DynamicListAPIView):
    queryset = iati.models.Sector.objects.all()
    serializer_class = serializers.SectorSerializer
    fields = ('url', 'code', 'name')


class SectorDetail(generics.DynamicRetrieveAPIView):
    queryset = iati.models.Sector.objects.all()
    serializer_class = serializers.SectorSerializer
