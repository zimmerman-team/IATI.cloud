from django.utils.http import urlunquote
from django.shortcuts import get_object_or_404
from rest_framework import generics
import iati
from api.organisation import serializers
from api.generics.views import DynamicListAPIView
from api.generics.views import DynamicRetrieveAPIView
from api.activity.views import ActivityList


def custom_get_object(self):
    """
    a custom version of view.get_object, to decode the url encoded by the
    OrganisationSerializer
    """
    queryset = self.filter_queryset(self.get_queryset())
    lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
    lookup_url = self.kwargs[lookup_url_kwarg]

    decoded_lookup_url = urlunquote(lookup_url)
    filter_kwargs = {self.lookup_field: decoded_lookup_url}
    return get_object_or_404(queryset, **filter_kwargs)


class OrganisationList(DynamicListAPIView):
    queryset = iati.models.Organisation.objects.all()
    serializer_class = serializers.OrganisationSerializer
    fields = ('url', 'code', 'name')


class OrganisationDetail(DynamicRetrieveAPIView):
    queryset = iati.models.Organisation.objects.all()
    serializer_class = serializers.OrganisationSerializer
    get_object = custom_get_object


class ParticipatedActivities(ActivityList):
    get_object = custom_get_object

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        organisation = iati.models.Organisation.objects.get(pk=pk)
        return organisation.activity_set.all()


class ReportedActivities(ActivityList):
    get_object = custom_get_object

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        organisation = iati.models.Organisation.objects.get(pk=pk)
        return organisation.activity_reporting_organisation.all()


class ProvidedTransactions(generics.ListAPIView):
    get_object = custom_get_object

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        organisation = iati.models.Organisation.objects.get(pk=pk)
        return organisation.transaction_providing_organisation.all()


class ReceivedTransactions(ActivityList):
    get_object = custom_get_object

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        organisation = iati.models.Organisation.objects.get(pk=pk)
        return organisation.transaction_receiving_organisation.all()
