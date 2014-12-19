import geodata
from api.city import serializers
from api.generics.views import DynamicListAPIView
from api.generics.views import DynamicRetrieveAPIView


class CityList(DynamicListAPIView):
    queryset = geodata.models.City.objects.all()
    serializer_class = serializers.CitySerializer
    fields = ('url', 'id', 'name')


class CityDetail(DynamicRetrieveAPIView):
    queryset = geodata.models.City.objects.all()
    serializer_class = serializers.CitySerializer
