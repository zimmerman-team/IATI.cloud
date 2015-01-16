import geodata
from api.country import serializers
from api.activity.views import ActivityList
from api.city.serializers import CitySerializer
from api.indicator.serializers import IndicatorSerializer
from geodata.models import Country
from indicator.models import IndicatorData
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView


class CountryList(ListAPIView):
    queryset = geodata.models.Country.objects.all()
    serializer_class = serializers.CountrySerializer
    fields = ('url', 'code', 'name')


class CountryDetail(RetrieveAPIView):
    queryset = geodata.models.Country.objects.all()
    serializer_class = serializers.CountrySerializer


class CountryActivities(ActivityList):
    def get_queryset(self):
        pk = self.kwargs.get('pk')
        country = Country.objects.get(pk=pk)
        return country.activity_set.all()


class CountryIndicators(ListAPIView):
    queryset = IndicatorData.objects.all()
    serializer_class = IndicatorSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        country = Country.objects.get(pk=pk)
        return country.indicatordata_set.all()


class CountryCities(ListAPIView):
    queryset = IndicatorData.objects.all()
    serializer_class = CitySerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        country = Country.objects.get(pk=pk)
        return country.city_set.all()