from rest_framework import generics
import iati
import serializers


class ActivityList(generics.ListAPIView):
    queryset = iati.models.Activity.objects.all()
    serializer_class = serializers.ActivityListSerializer
