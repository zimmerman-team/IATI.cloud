
import geodata
from iati.models import Activity
from api.region import serializers
from rest_framework import generics
from api.country.serializers import CountrySerializer
from api.activity.views import ActivityList
from api.generics.views import DynamicListAPIView
from api.generics.views import DynamicRetrieveAPIView


class RegionList(DynamicListAPIView):
    queryset = geodata.models.Region.objects.all()
    serializer_class = serializers.RegionSerializer
    fields = ('url', 'code', 'name')


class RegionDetail(DynamicRetrieveAPIView):
    queryset = geodata.models.Region.objects.all()
    serializer_class = serializers.RegionSerializer


class RegionCountries(DynamicListAPIView):
    serializer_class = CountrySerializer
    fields = ('url', 'code', 'name')

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        region = geodata.models.Region.objects.get(pk=pk)
        return region.countries


class RegionActivities(ActivityList):
    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Activity.objects.in_region(pk)
