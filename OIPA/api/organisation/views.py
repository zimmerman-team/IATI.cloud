from api import generics
import iati
from api.organisation import serializers


class OrganisationList(generics.DynamicListAPIView):
    queryset = iati.models.Organisation.objects.all()
    serializer_class = serializers.OrganisationSerializer
    fields = ('url', 'code', 'name')


class OrganisationDetail(generics.DynamicRetrieveAPIView):
    queryset = iati.models.Organisation.objects.all()
    serializer_class = serializers.OrganisationSerializer
