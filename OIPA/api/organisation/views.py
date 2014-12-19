import iati
from api.organisation import serializers
from api.generics.views import DynamicListAPIView
from api.generics.views import DynamicRetrieveAPIView


class OrganisationList(DynamicListAPIView):
    queryset = iati.models.Organisation.objects.all()
    serializer_class = serializers.OrganisationSerializer
    fields = ('url', 'code', 'name')


class OrganisationDetail(DynamicRetrieveAPIView):
    queryset = iati.models.Organisation.objects.all()
    serializer_class = serializers.OrganisationSerializer
