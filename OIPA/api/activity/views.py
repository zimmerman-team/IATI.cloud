from rest_framework import generics
import iati
from api.activity import serializers


class ActivityList(generics.ListAPIView):
    queryset = iati.models.Activity.objects.all()
    serializer_class = serializers.ActivityListSerializer


class ActivityDetail(generics.RetrieveAPIView):
    queryset = iati.models.Activity.objects.all()
    serializer_class = serializers.ActivityDetailSerializer


class ActivitySectors(generics.ListAPIView):
    serializer_class = serializers.ActivitySectorSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return iati.models.Activity(pk=pk).activitysector_set.all()
