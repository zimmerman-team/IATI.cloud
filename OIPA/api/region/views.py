import geodata
from api.region import serializers
from api.generics.views import DynamicListAPIView
from api.generics.views import DynamicRetrieveAPIView


class RegionList(DynamicListAPIView):
    queryset = geodata.models.Region.objects.all()
    serializer_class = serializers.RegionSerializer
    fields = ('url', 'code', 'name')


class RegionDetail(DynamicRetrieveAPIView):
    queryset = geodata.models.Region.objects.all()
    serializer_class = serializers.RegionSerializer
