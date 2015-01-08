import iati
from api.generics.views import DynamicListAPIView
from api.generics.views import DynamicRetrieveAPIView
from api.sector import serializers
from api.activity.views import ActivityList


class SectorList(DynamicListAPIView):
    queryset = iati.models.Sector.objects.all()
    serializer_class = serializers.SectorSerializer
    fields = ('url', 'code', 'name')


class SectorDetail(DynamicRetrieveAPIView):
    queryset = iati.models.Sector.objects.all()
    serializer_class = serializers.SectorSerializer


class SectorActivities(ActivityList):
    def get_queryset(self):
        pk = self.kwargs.get('pk')
        sector = iati.models.Sector.objects.get(pk=pk)
        return sector.activity_set.all()
