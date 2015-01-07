from django.utils.http import urlunquote
from django.shortcuts import get_object_or_404
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

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup_url = self.kwargs[lookup_url_kwarg]

        decoded_lookup_url = urlunquote(lookup_url)
        filter_kwargs = {self.lookup_field: decoded_lookup_url}

        return get_object_or_404(queryset, **filter_kwargs)
