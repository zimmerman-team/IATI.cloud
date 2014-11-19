from rest_framework import generics
import geodata
from api.country import serializers


class CountryList(generics.ListAPIView):
    queryset = geodata.models.Country.objects.all()
    serializer_class = serializers.CountryListSerializer


class CountryDetail(generics.RetrieveAPIView):
    queryset = geodata.models.Country.objects.all()
    serializer_class = serializers.CountryDetailSerializer
