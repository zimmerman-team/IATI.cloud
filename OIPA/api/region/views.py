from rest_framework import generics
import geodata
from api.region import serializers


class RegionList(generics.ListAPIView):
    queryset = geodata.models.Region.objects.all()
    serializer_class = serializers.RegionListSerializer


class RegionDetail(generics.RetrieveAPIView):
    queryset = geodata.models.Region.objects.all()
    serializer_class = serializers.RegionDetailSerializer
