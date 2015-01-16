import geodata
from api.city import serializers
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView


class CityList(ListAPIView):
    queryset = geodata.models.City.objects.all()
    serializer_class = serializers.CitySerializer
    fields = ('url', 'id', 'name')


class CityDetail(RetrieveAPIView):
    queryset = geodata.models.City.objects.all()
    serializer_class = serializers.CitySerializer
