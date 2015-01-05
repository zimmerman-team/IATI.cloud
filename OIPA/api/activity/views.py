from rest_framework import generics
from iati.models import Activity
from api.activity import serializers
from api.generics.views import DynamicListAPIView
from api.generics.views import DynamicRetrieveAPIView
from api.generics.filters import BasicFilterBackend
from api.generics.filters import SearchFilter
from rest_framework.filters import OrderingFilter
from api.activity import filters


class ActivityList(DynamicListAPIView):
    queryset = Activity.objects.all()
    filter_backends = (SearchFilter, BasicFilterBackend, OrderingFilter,)
    filter_class = filters.ActivityFilter
    serializer_class = serializers.ActivitySerializer
    fields = ['url', 'id', 'title', 'total_budget']


class ActivityDetail(DynamicRetrieveAPIView):
    queryset = Activity.objects.all()
    serializer_class = serializers.ActivitySerializer


class ActivitySectors(generics.ListAPIView):
    serializer_class = serializers.ActivitySectorSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Activity(pk=pk).activitysector_set.all()


class ActivityParticipatingOrganisations(generics.ListAPIView):
    serializer_class = serializers.ParticipatingOrganisationSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Activity(pk=pk).participating_organisations.all()


class ActivityRecipientCountry(generics.ListAPIView):
    serializer_class = serializers.RecipientCountrySerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Activity(pk=pk).activityrecipientcountry_set.all()
