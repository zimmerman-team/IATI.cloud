from api import generics
import geodata
from api.country import serializers


class CountryList(generics.DynamicListAPIView):
    queryset = geodata.models.Country.objects.all()
    serializer_class = serializers.CountrySerializer
    fields = ('url', 'code', 'name')


class CountryDetail(generics.DynamicRetrieveAPIView):
    queryset = geodata.models.Country.objects.all()
    serializer_class = serializers.CountrySerializer
