import geodata
from api.country import serializers
from api.generics.views import DynamicListAPIView
from api.generics.views import DynamicRetrieveAPIView


class CountryList(DynamicListAPIView):
    queryset = geodata.models.Country.objects.all()
    serializer_class = serializers.CountrySerializer
    fields = ('url', 'code', 'name')


class CountryDetail(DynamicRetrieveAPIView):
    queryset = geodata.models.Country.objects.all()
    serializer_class = serializers.CountrySerializer
