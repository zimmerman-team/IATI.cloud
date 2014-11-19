from rest_framework import generics
import geodata
from api.city import serializers


class CityList(generics.ListAPIView):
    queryset = geodata.models.City.objects.all()
    serializer_class = serializers.CityListSerializer


class CityDetail(generics.RetrieveAPIView):
    queryset = geodata.models.City.objects.all()
    serializer_class = serializers.CityDetailSerializer
