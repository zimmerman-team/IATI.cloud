from rest_framework import generics
import iati
from api.activity import serializers
import api.generics


class ActivityList(api.generics.DynamicListAPIView):
    queryset = iati.models.Activity.objects.all()
    serializer_class = serializers.ActivitySerializer
    fields = ['url', 'id', 'title', 'total_budget']


class ActivityDetail(api.generics.DynamicRetrieveAPIView):
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
