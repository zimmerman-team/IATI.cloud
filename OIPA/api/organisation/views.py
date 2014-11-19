from rest_framework import generics
import iati
from api.organisation import serializers


class OrganisationList(generics.ListAPIView):
    queryset = iati.models.Organisation.objects.all()
    serializer_class = serializers.OrganisationListSerializer


class OrganisationDetail(generics.RetrieveAPIView):
    queryset = iati.models.Organisation.objects.all()
    serializer_class = serializers.OrganisationDetailSerializer
