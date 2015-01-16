from django.utils.http import urlunquote
from django.shortcuts import get_object_or_404
import iati
from api.organisation import serializers
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from api.activity.views import ActivityList
from api.transaction.views import TransactionList


def custom_get_object(self):
    """
    a custom version of view.get_object, to decode the url encoded by the
    OrganisationSerializer
    """
    queryset = self.filter_queryset(self.get_queryset())
    return custom_get_object_from_queryset(self, queryset)

def custom_get_object_from_queryset(self, queryset):
    lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
    lookup_url = self.kwargs[lookup_url_kwarg]

    decoded_lookup_url = urlunquote(lookup_url)
    filter_kwargs = {self.lookup_field: decoded_lookup_url}
    return get_object_or_404(queryset, **filter_kwargs)


class OrganisationList(ListAPIView):
    queryset = iati.models.Organisation.objects.all()
    serializer_class = serializers.OrganisationSerializer
    fields = ('url', 'code', 'name')


class OrganisationDetail(RetrieveAPIView):
    queryset = iati.models.Organisation.objects.all()
    serializer_class = serializers.OrganisationSerializer
    get_object = custom_get_object


class ParticipatedActivities(ActivityList):

    def get_queryset(self):
        organisation = custom_get_object_from_queryset(self,
            iati.models.Organisation.objects.all())
        return organisation.activity_set.all()


class ReportedActivities(ActivityList):
    def get_queryset(self):
        organisation = custom_get_object_from_queryset(self,
            iati.models.Organisation.objects.all())
        return organisation.activity_reporting_organisation.all()


class ProvidedTransactions(TransactionList):

    def get_queryset(self):
        organisation = custom_get_object_from_queryset(self,
            iati.models.Organisation.objects.all())
        return organisation.transaction_providing_organisation.all()


class ReceivedTransactions(TransactionList):

    def get_queryset(self):
        organisation = custom_get_object_from_queryset(self,
            iati.models.Organisation.objects.all())
        return organisation.transaction_receiving_organisation.all()
