from rest_framework import generics
import iati
from api.sector import serializers


class SectorList(generics.ListAPIView):
    queryset = iati.models.Sector.objects.all()
    serializer_class = serializers.SectorListSerializer


class SectorDetail(generics.RetrieveAPIView):
    queryset = iati.models.Sector.objects.all()
    serializer_class = serializers.SectorDetailSerializer
