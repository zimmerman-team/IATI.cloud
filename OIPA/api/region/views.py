from api import generics
import geodata
from api.region import serializers


class RegionList(generics.DynamicListAPIView):
    queryset = geodata.models.Region.objects.all()
    serializer_class = serializers.RegionSerializer
    fields = ('url', 'code', 'name')


class RegionDetail(generics.DynamicRetrieveAPIView):
    queryset = geodata.models.Region.objects.all()
    serializer_class = serializers.RegionSerializer
