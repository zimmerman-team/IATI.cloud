import geodata
from rest_framework import generics
from api.country import serializers
from api.generics.views import DynamicListAPIView
from api.generics.views import DynamicRetrieveAPIView
from api.activity.views import ActivityList
from api.city.serializers import CitySerializer
from api.indicator.serializers import IndicatorSerializer
from geodata.models import Country
from indicator.models import IndicatorData


class CountryList(DynamicListAPIView):
    queryset = geodata.models.Country.objects.all()
    serializer_class = serializers.CountrySerializer
    fields = ('url', 'code', 'name')


class CountryDetail(DynamicRetrieveAPIView):
    queryset = geodata.models.Country.objects.all()
    serializer_class = serializers.CountrySerializer


class CountryActivities(ActivityList):
    def get_queryset(self):
        pk = self.kwargs.get('pk')
        country = Country.objects.get(pk=pk)
        return country.activity_set.all()


class CountryIndicators(generics.ListAPIView):
    queryset = IndicatorData.objects.all()
    serializer_class = IndicatorSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        country = Country.objects.get(pk=pk)
        return country.indicatordata_set.all()


class CountryCities(generics.ListAPIView):
    queryset = IndicatorData.objects.all()
    serializer_class = CitySerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        country = Country.objects.get(pk=pk)
        return country.city_set.all()