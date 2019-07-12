import rest_framework
from django.shortcuts import get_object_or_404
from django.utils.http import urlunquote
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import authentication, status
from rest_framework.generics import (
    ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from api.activity.views import ActivityList
from api.generics.views import (
    DynamicDetailCRUDView, DynamicDetailView, DynamicListCRUDView,
    DynamicListView
)
from api.organisation import serializers
from api.organisation.validators import organisation_required_fields
from api.publisher.permissions import PublisherPermissions
from api.renderers import (
    OrganisationIATICSVRenderer, OrganisationIATIXMLRenderer
)
from api.transaction.views import TransactionList
from iati_organisation.models import (
    DocumentLinkRecipientCountry, Organisation, OrganisationDocumentLink,
    OrganisationDocumentLinkCategory, OrganisationDocumentLinkLanguage,
    RecipientCountryBudget, RecipientCountryBudgetLine, RecipientOrgBudget,
    RecipientOrgBudgetLine, RecipientRegionBudget, RecipientRegionBudgetLine,
    TotalBudget, TotalBudgetLine, TotalExpenditure, TotalExpenditureLine
)


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


class FilterPublisherMixin(object):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        publisher_id = self.kwargs.get('publisher_id')

        return Organisation.objects.filter(publisher__id=publisher_id)


class OrganisationList(DynamicListView):
    """
    Returns a list of IATI Organisations stored in OIPA.

    ## Result details

    Each result item contains short information about organisation
    including URI to organisation details.

    URI is constructed as follows: `/api/organisations/{organisation_id}`

    """
    renderer_classes = (
        rest_framework.renderers.BrowsableAPIRenderer,
        rest_framework.renderers.JSONRenderer,
        OrganisationIATIXMLRenderer,
        OrganisationIATICSVRenderer,
    )
    queryset = Organisation.objects.all()
    serializer_class = serializers.OrganisationSerializer
    selectable_fields = ()
    fields = ('url', 'organisation_identifier',
              'last_updated_datetime', 'name')


class OrganisationDetail(CacheResponseMixin, DynamicDetailView):
    """
    Returns detailed information about Organisation.

    ## URI Format

    ```
    /api/organisations/{organisation_id}
    ```

    ### URI Parameters

    - `organisation_id`: Numerical ID of desired Organisation

    ## Request parameters

    - `fields` (*optional*): List of fields to display

    """
    renderer_classes = (
        rest_framework.renderers.BrowsableAPIRenderer,
        rest_framework.renderers.JSONRenderer,
        OrganisationIATIXMLRenderer,
        OrganisationIATICSVRenderer,
    )
    queryset = Organisation.objects.all()
    serializer_class = serializers.OrganisationSerializer


class OrganisationMarkReadyToPublish(APIView, FilterPublisherMixin):

    authentication_classes = (authentication.TokenAuthentication,)

    def post(self, request, publisher_id, pk):
        organisation = Organisation.objects.get(pk=pk)

        if (organisation.ready_to_publish):
            organisation.ready_to_publish = False
            organisation.modified = True
            organisation.save()
            return Response(False)

        # TODO: check if organisation is valid for publishing- 2017-01-24
        if not organisation_required_fields(organisation):
            return Response({
                'error': True,
                'content': 'Not all required fields are on the organisation'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        organisation.ready_to_publish = True
        organisation.modified = True
        organisation.save()

        return Response(True)


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
            self, Organisation.objects.all())
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
            self, Organisation.objects.all())
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
            self, Organisation.objects.all())
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
            self, Organisation.objects.all())
        return organisation.transaction_receiving_organisation.all()


class UpdateOrganisationSearchMixin(object):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def reindex_organisation(self, serializer):
        instance = serializer.instance.get_organisation()
        self.reindex_organisation(instance)

    def perform_create(self, serializer):
        serializer.save()
        self.reindex_organisation(serializer)

    def perform_update(self, serializer):
        serializer.save()
        self.reindex_organisation(serializer)


class OrganisationListCRUD(FilterPublisherMixin, DynamicListCRUDView):
    queryset = Organisation.objects.all()
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

    All information on organisation transactions can be found on a separate
    page:

    - `/api/activities/{organisation_id}/transactions/`:
        List of transactions.
    - `/api/activities/{organisation_id}/provider-organisation-tree/`:
        The upward and downward provider-organisation-id traceability tree of
        this organisation.

    ## Request parameters

    - `fields` (*optional*): List of fields to display

    """
    queryset = Organisation.objects.all()
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
            return Organisation.objects.get(pk=pk).total_budgets.all()
        except Organisation.DoesNotExist:
            return None


class OrganisationTotalBudgetDetailCRUD(RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.OrganisationTotalBudgetSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        return TotalBudget.objects.get(pk=pk)


class OrganisationTotalBudgetBudgetLineListCRUD(ListCreateAPIView):
    serializer_class = serializers.TotalBudgetBudgetLineSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('total_budget_id')
        try:
            return TotalBudget.objects.get(pk=pk).totalbudgetline_set.all()
        except Organisation.DoesNotExist:
            return None


class OrganisationTotalBudgetBudgetLineDetailCRUD(
        RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.TotalBudgetBudgetLineSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        return TotalBudgetLine.objects.get(pk=pk)


class OrganisationRecipientOrgBudgetListCRUD(ListCreateAPIView):
    serializer_class = serializers.OrganisationRecipientOrgBudgetSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        try:
            return Organisation.objects.get(pk=pk).recipientorgbudget_set.all()
        except Organisation.DoesNotExist:
            return None


class OrganisationRecipientOrgBudgetDetailCRUD(RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.OrganisationRecipientOrgBudgetSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        return RecipientOrgBudget.objects.get(pk=pk)


class OrganisationRecipientOrgBudgetBudgetLineListCRUD(ListCreateAPIView):
    serializer_class = serializers.RecipientOrgBudgetLineSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('recipient_org_budget_id')
        try:
            return TotalBudget.objects.get(
                pk=pk
            ).recipientorgbudgetline_set.all()
        except Organisation.DoesNotExist:
            return None


class OrganisationRecipientOrgBudgetBudgetLineDetailCRUD(
        RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.RecipientOrgBudgetLineSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        return RecipientOrgBudgetLine.objects.get(pk=pk)


class OrganisationRecipientCountryBudgetListCRUD(ListCreateAPIView):
    serializer_class = serializers.OrganisationRecipientCountryBudgetSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        try:
            return Organisation.objects.get(
                pk=pk
            ).recipientcountrybudget_set.all()
        except Organisation.DoesNotExist:
            return None


class OrganisationRecipientCountryBudgetDetailCRUD(
        RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.OrganisationRecipientCountryBudgetSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        return RecipientCountryBudget.objects.get(pk=pk)


class OrganisationRecipientCountryBudgetBudgetLineListCRUD(ListCreateAPIView):
    serializer_class = serializers.RecipientCountryBudgetLineSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('recipient_country_budget_id')
        try:
            return RecipientCountryBudget.objects.get(
                pk=pk).recipientcountrybudgetline_set.all()
        except Organisation.DoesNotExist:
            return None


class OrganisationRecipientCountryBudgetBudgetLineDetailCRUD(
        RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.RecipientCountryBudgetLineSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        return RecipientCountryBudgetLine.objects.get(pk=pk)


class OrganisationRecipientRegionBudgetListCRUD(ListCreateAPIView):
    serializer_class = serializers.OrganisationRecipientRegionBudgetSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        try:
            return Organisation.objects.get(
                pk=pk
            ).recipientregionbudget_set.all()
        except Organisation.DoesNotExist:
            return None


class OrganisationRecipientRegionBudgetDetailCRUD(
        RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.OrganisationRecipientRegionBudgetSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        return RecipientRegionBudget.objects.get(pk=pk)


class OrganisationRecipientRegionBudgetBudgetLineListCRUD(ListCreateAPIView):
    serializer_class = serializers.RecipientRegionBudgetLineSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('recipient_region_budget_id')
        try:
            return RecipientRegionBudget.objects.get(
                pk=pk).recipientregionbudgetline_set.all()
        except Organisation.DoesNotExist:
            return None


class OrganisationRecipientRegionBudgetBudgetLineDetailCRUD(
        RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.RecipientRegionBudgetLineSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        return RecipientRegionBudgetLine.objects.get(pk=pk)


class OrganisationTotalExpenditureListCRUD(ListCreateAPIView):
    serializer_class = serializers.OrganisationTotalExpenditureSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        try:
            return Organisation.objects.get(pk=pk).totalexpenditure_set.all()
        except Organisation.DoesNotExist:
            return None


class OrganisationTotalExpenditureDetailCRUD(RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.OrganisationTotalExpenditureSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        return TotalExpenditure.objects.get(pk=pk)


class OrganisationTotalExpenditureExpenseLineListCRUD(ListCreateAPIView):
    serializer_class = serializers.TotalExpenditureLineSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('total_expenditure_id')
        try:
            return TotalExpenditure.objects.get(
                pk=pk
            ).totalexpenditureline_set.all()
        except Organisation.DoesNotExist:
            return None


class OrganisationTotalExpenditureExpenseLineDetailCRUD(
        RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.TotalExpenditureLineSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        return TotalExpenditureLine.objects.get(pk=pk)


class OrganisationDocumentLinkList(ListCreateAPIView):
    serializer_class = serializers.OrganisationDocumentLinkSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        try:
            return Organisation.objects.get(pk=pk).documentlink_set.all()
        except Organisation.DoesNotExist:
            return None


class OrganisationDocumentLinkDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.OrganisationDocumentLinkSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        return OrganisationDocumentLink.objects.get(pk=pk)


class OrganisationDocumentLinkCategoryList(ListCreateAPIView):
    serializer_class = serializers.OrganisationDocumentLinkCategorySerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('document_link_id')
        return OrganisationDocumentLink(pk=pk).documentlinkcategory_set.all()


class OrganisationDocumentLinkCategoryDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.OrganisationDocumentLinkCategorySerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('category_id')
        return OrganisationDocumentLinkCategory.objects.get(pk=pk)


class OrganisationDocumentLinkLanguageList(ListCreateAPIView):
    serializer_class = serializers.OrganisationDocumentLinkLanguageSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('document_link_id')
        return OrganisationDocumentLink(pk=pk).documentlinklanguage_set.all()


class OrganisationDocumentLinkLanguageDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.OrganisationDocumentLinkLanguageSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('language_id')
        return OrganisationDocumentLinkLanguage.objects.get(pk=pk)


class OrganisationDocumentLinkRecipientCountryList(ListCreateAPIView):
    serializer_class = serializers\
        .OrganisationDocumentLinkRecipientCountrySerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('document_link_id')
        return OrganisationDocumentLink(
            pk=pk
        ).documentlinkrecipient_country_set.all()


class OrganisationDocumentLinkRecipientCountryDetail(
        RetrieveUpdateDestroyAPIView):
    serializer_class = serializers\
        .OrganisationDocumentLinkRecipientCountrySerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('recipient_country_id')
        return DocumentLinkRecipientCountry.objects.get(pk=pk)


class OrganisationFileOrganisationDocumentLinkList(ListAPIView):
    """
    This endpoint is related to Organisation File for public request

    ## URI Format

    ```
    /api/organisations/organisation-file/{organisation_identifier}
    /organisation-document-link-list/
    ```

    ### URI Parameters

    - `organisation_identifier`: IATI Organisation Identifier
    """
    serializer_class = serializers.OrganisationDocumentLinkSerializer

    def get_queryset(self):
        organisation_identifier = self.kwargs.get('organisation_identifier')
        try:
            return Organisation.objects.get(
                organisation_identifier=organisation_identifier
            ).organisationdocumentlink_set.all().order_by('id')
        except Organisation.DoesNotExist:
            return None
