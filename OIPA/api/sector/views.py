import iati
from api.generics.views import DynamicListAPIView
from api.generics.views import DynamicRetrieveAPIView
from api.sector import serializers


class SectorList(DynamicListAPIView):
    queryset = iati.models.Sector.objects.all()
    serializer_class = serializers.SectorSerializer
    fields = ('url', 'code', 'name')


class SectorDetail(DynamicRetrieveAPIView):
    queryset = iati.models.Sector.objects.all()
    serializer_class = serializers.SectorSerializer
