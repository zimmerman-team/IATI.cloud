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
    """
    Returns a list of IATI Organisations stored in OIPA.

    ## Result details

    Each result item contains short information about organisation
    including URI to city details.

    URI is constructed as follows: `/api/organisations/{organisation_id}`

    """
    queryset = iati.models.Organisation.objects.all()
    serializer_class = serializers.OrganisationSerializer
    fields = ('url', 'code', 'name')


class OrganisationDetail(RetrieveAPIView):
    """
    Returns detailed information about Organisation.

    ## URI Format

    ```
    /api/organisations/{city_id}
    ```

    ### URI Parameters

    - `organisation_id`: Numerical ID of desired Organisation

    ## Request parameters

    - `fields` (*optional*): List of fields to display

    """
    queryset = iati.models.Organisation.objects.all()
    serializer_class = serializers.OrganisationSerializer
    get_object = custom_get_object


class ParticipatedActivities(ActivityList):
    """
    Returns a list of IATI Activities Organisation participated in.

    ## URI Format

    ```
    /api/organisations/{organisation_id}/participated-activities
    ```

    ### URI Parameters

    - `organisation_id`: Numerical ID of desired Organisation

    ## Result details

    Each result item contains short information about activity including URI
    to activity details.

    URI is constructed as follows: `/api/activities/{activity_id}`

    """
    def get_queryset(self):
        organisation = custom_get_object_from_queryset(self,
            iati.models.Organisation.objects.all())
        return organisation.activity_set.all()


class ReportedActivities(ActivityList):
    """
    Returns a list of IATI Activities Organisation reported.

    ## URI Format

    ```
    /api/organisations/{organisation_id}/reported-activities
    ```

    ### URI Parameters

    - `organisation_id`: Numerical ID of desired Organisation

    ## Result details

    Each result item contains short information about activity including URI
    to activity details.

    URI is constructed as follows: `/api/activities/{activity_id}`

    """
    def get_queryset(self):
        organisation = custom_get_object_from_queryset(self,
            iati.models.Organisation.objects.all())
        return organisation.activity_reporting_organisation.all()


class ProvidedTransactions(TransactionList):
    """
    Returns a list of IATI Transactions provided by Organisation.

    ## URI Format

    ```
    /api/organisations/{organisation_id}/provided-transactions
    ```

    ### URI Parameters

    - `organisation_id`: Numerical ID of desired Organisation

    ## Result details

    Each result item contains short information about transaction including URI
    to transaction details.

    URI is constructed as follows: `/api/transactions/{activity_id}`

    """
    def get_queryset(self):
        organisation = custom_get_object_from_queryset(self,
            iati.models.Organisation.objects.all())
        return organisation.transaction_providing_organisation.all()


class ReceivedTransactions(TransactionList):
    """
    Returns a list of IATI Transactions received by Organisation.

    ## URI Format

    ```
    /api/organisations/{organisation_id}/received-transactions
    ```

    ### URI Parameters

    - `organisation_id`: Numerical ID of desired Organisation

    ## Result details

    Each result item contains short information about transaction including URI
    to transaction details.

    URI is constructed as follows: `/api/transactions/{activity_id}`

    """
    def get_queryset(self):
        organisation = custom_get_object_from_queryset(self,
            iati.models.Organisation.objects.all())
        return organisation.transaction_receiving_organisation.all()
