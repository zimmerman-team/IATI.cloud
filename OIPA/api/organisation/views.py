from django.utils.http import urlunquote
from django.shortcuts import get_object_or_404
from iati_organisation import models

from api.organisation import serializers
from rest_framework.generics import ListAPIView, RetrieveAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, GenericAPIView
from rest_framework.filters import DjangoFilterBackend
from api.activity.views import ActivityList
from api.transaction.views import TransactionList

from api.generics.views import DynamicListView, DynamicDetailView, DynamicListCRUDView, DynamicDetailCRUDView

from rest_framework import authentication, permissions
from api.publisher.permissions import OrganisationAdminGroupPermissions, PublisherPermissions
from rest_framework.response import Response
from rest_framework import status


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


class OrganisationList(DynamicListView):
    """
    Returns a list of IATI Organisations stored in OIPA.

    ## Result details

    Each result item contains short information about organisation
    including URI to city details.

    URI is constructed as follows: `/api/organisations/{organisation_id}`

    """
    queryset = models.Organisation.objects.all()
    serializer_class = serializers.OrganisationSerializer
    fields = ('url', 'organisation_identifier','last_updated_datetime', 'name')

class OrganisationDetail(DynamicDetailView):
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
    queryset = models.Organisation.objects.all()
    serializer_class = serializers.OrganisationSerializer


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
        organisation = custom_get_object_from_queryset(
            self, organisation.models.Organisation.objects.all())
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
        organisation = custom_get_object_from_queryset(
            self, organisation.models.Organisation.objects.all())
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
        organisation = custom_get_object_from_queryset(
            self, organisation.models.Organisation.objects.all())
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
        organisation = custom_get_object_from_queryset(
            self, organisation.models.Organisation.objects.all())
        return organisation.transaction_receiving_organisation.all()



class FilterPublisherMixin(object):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        publisher_id = self.kwargs.get('publisher_id')

        return Organisation.objects.filter(publisher__id=publisher_id)

class UpdateOrganisationSearchMixin(object):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def reindex_organisation(self, serializer):
        instance = serializer.instance.get_organisation()
        reindex_organisation(instance)

    def perform_create(self, serializer):
        serializer.save()
        self.reindex_organisation(serializer)

    def perform_update(self, serializer):
        serializer.save()
        self.reindex_organisation(serializer)



class OrganisationListCRUD(FilterPublisherMixin, DynamicListCRUDView):
    queryset = models.Organisation.objects.all()
    filter_backends = (DjangoFilterBackend,)
    # filter_class = filters.OrganisationFilter
    serializer_class = serializers.OrganisationSerializer

    # TODO: define authentication_classes globally? - 2017-01-05
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    always_ordering = 'id'

    ordering_fields = (
        'title',
        'recipient_country',
        'planned_start_date',
        'actual_start_date',
        'planned_end_date',
        'actual_end_date',
        'start_date',
        'end_date',
        'organisation_budget_value',
        'organisation_incoming_funds_value',
        'organisation_disbursement_value',
        'organisation_expenditure_value',
        'organisation_plus_child_budget_value')


class OrganisationDetailCRUD(DynamicDetailCRUDView):
    """
    Returns detailed information about Organisation.

    ## URI Format

    ```
    /api/activities/{organisation_id}
    ```

    ### URI Parameters

    - `organisation_id`: Desired organisation ID

    ## Extra endpoints

    All information on organisation transactions can be found on a separate page:

    - `/api/activities/{organisation_id}/transactions/`:
        List of transactions.
    - `/api/activities/{organisation_id}/provider-organisation-tree/`:
        The upward and downward provider-organisation-id traceability tree of this organisation.

    ## Request parameters

    - `fields` (*optional*): List of fields to display

    """
    queryset = models.Organisation.objects.all()
    # filter_class = filters.OrganisationFilter
    serializer_class = serializers.OrganisationSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )


class OrganisationTotalBudgetListCRUD(ListCreateAPIView):
    serializer_class = serializers.OrganisationTotalBudgetSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        try:
            return models.Organisation.objects.get(pk=pk).total_budgets.all()
        except Organisation.DoesNotExist:
            return None

class OrganisationTotalBudgetDetailCRUD(RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.OrganisationTotalBudgetSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        return models.TotalBudget.objects.get(pk=pk)


class OrganisationRecipientOrgBudgetListCRUD(ListCreateAPIView):
    serializer_class = serializers.OrganisationRecipientOrgBudgetSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        try:
            return models.Organisation.objects.get(pk=pk).recipientorgbudget_set.all()
        except Organisation.DoesNotExist:
            return None

class OrganisationRecipientOrgBudgetDetailCRUD(RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.OrganisationRecipientOrgBudgetSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        return models.RecipientOrgBudget.objects.get(pk=pk)
