import geodata
from api.country import serializers
from api.generics.views import DynamicListAPIView
from api.generics.views import DynamicRetrieveAPIView
from api.activity.views import ActivityList
from iati.models import Activity
from geodata.models import Country


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
        return country.activity_set
