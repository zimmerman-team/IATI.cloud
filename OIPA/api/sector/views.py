import iati
from rest_framework import generics
from api.sector import serializers
from api.activity.views import ActivityList
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView


class SectorList(ListAPIView):
    queryset = iati.models.Sector.objects.all()
    serializer_class = serializers.SectorSerializer
    fields = ('url', 'code', 'name')


class SectorDetail(RetrieveAPIView):
    queryset = iati.models.Sector.objects.all()
    serializer_class = serializers.SectorSerializer


class SectorActivities(ActivityList):
    def get_queryset(self):
        pk = self.kwargs.get('pk')
        sector = iati.models.Sector.objects.get(pk=pk)
        return sector.activity_set.all()
