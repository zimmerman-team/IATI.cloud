from rest_framework import generics
import iati
from api.activity import serializers
from api.generics import filters
from api.generics.views import DynamicListAPIView
from api.generics.views import DynamicRetrieveAPIView


class ActivityList(DynamicListAPIView):
    queryset = iati.models.Activity.objects.all()
    filter_backends = (filters.SearchFilter,)
    serializer_class = serializers.ActivitySerializer
    fields = ['url', 'id', 'title', 'total_budget']


class ActivityDetail(DynamicRetrieveAPIView):
    queryset = iati.models.Activity.objects.all()
    serializer_class = serializers.ActivitySerializer


class ActivitySectors(generics.ListAPIView):
    serializer_class = serializers.ActivitySectorSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return iati.models.Activity(pk=pk).activitysector_set.all()


class ActivityParticipatingOrganisations(generics.ListAPIView):
    serializer_class = serializers.ParticipatingOrganisationSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return iati.models.Activity(pk=pk).participating_organisations.all()


class ActivityRecipientCountry(generics.ListAPIView):
    serializer_class = serializers.RecipientCountrySerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return iati.models.Activity(pk=pk).activityrecipientcountry_set.all()
