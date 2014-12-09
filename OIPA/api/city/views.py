from api import generics
import geodata
from api.city import serializers


class CityList(generics.DynamicListAPIView):
    queryset = geodata.models.City.objects.all()
    serializer_class = serializers.CitySerializer
    fields = ('url', 'id', 'name')


class CityDetail(generics.DynamicRetrieveAPIView):
    queryset = geodata.models.City.objects.all()
    serializer_class = serializers.CitySerializer
