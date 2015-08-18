from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView, GenericAPIView
from iati.models import Activity
from api.activity import serializers
from api.activity import filters
from api.activity.aggregation import AggregationsPaginationSerializer
from api.generics.filters import BasicFilterBackend
from api.generics.filters import SearchFilter
from rest_framework.filters import DjangoFilterBackend

from api.transaction.serializers import TransactionSerializer

import json
from rest_framework.response import Response
from django.db.models import Count, Sum
from rest_framework import mixins, status

from django.db.models import Q

class ActivityAggregations(GenericAPIView):

    queryset = Activity.objects.all()

    filter_backends = (SearchFilter, BasicFilterBackend, OrderingFilter,)
    filter_class = filters.ActivityFilter
    # serializer_class = serializers.AggregationSerializer
    # fields = ('url', 'id', 'title', 'total_budget')
    # pagination_serializer_class = AggregationsPaginationSerializer

    aggregationAnnotates = {
        "count": Count('id'),
        "total_budget": Sum('total_budget'),
        "disbursement": Sum('transaction__value'),
        "expenditure": Sum('transaction__value'),
        "commitment": Sum('transaction__value'),
        "incoming_fund": Sum('transaction__value'),
    }

    aggregationFilters = {
        "count": Q(),
        "total_budget": Q(),
        "disbursement": Q(transaction__transaction_type='D'),
        "expenditure": Q(transaction__transaction_type='E'),
        "commitment": Q(transaction__transaction_type='C'),
        "incoming_fund": Q(transaction__transaction_type='IF'),
    }

    aggregationValues = (
        "recipient_country",
        "recipient_region",
        "sector",
    )

    def aggregate_disbursement(self):
        queryset = self.filter(transaction__transaction_type='D')
        sum = queryset.aggregate(
            disbursement=Sum('transaction__value')
        ).get('disbursement', 0.00)
        return sum

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        values = request.query_params.get('values')
        annotates = request.query_params.get('annotates')
        # sort = request.query_params.get('sort_by')

        if (values and annotates):

            # parse annotates
            def fillAnnotateDict(annotates):
                annotateList = annotates.split(',')
                annotateDict = {}

                for k,v in self.aggregationAnnotates.iteritems():
                    if k in annotateList:
                        annotateDict[k] = v

                return annotateDict

            def fillFilterList(annotates):
                annotateList = annotates.split(',')
                filterList = []

                for k,v in self.aggregationFilters.iteritems():
                    if k in annotateList:
                        filterList.append(v)

                return filterList

            def fillValueList(values):
                values = values.split(',')
                valuesList = []

                for v in values: 
                    if v in self.aggregationValues:
                        valuesList.append(v)

                return valuesList

            # values to group on
            valuesList = fillValueList(values)
            annotateDict = fillAnnotateDict(annotates)
            filterList = fillFilterList(annotates)

            print(valuesList)
            print(annotateDict)
            print(filterList)

            if (valuesList):
                # todo: annotate orignal geo object
                valuesQuerySet = queryset \
                    .filter(*filterList) \
                    .values(*valuesList) \
                    .annotate(**annotateDict)

                return Response(valuesQuerySet)
            else:
                return Response('specified value is invalid', status.HTTP_404_NOT_FOUND)


            # serializer = self.serializer_class(queryset)
            # return Response(serializer.data)        


            return Response(json.dumps(list(valuesQuerySet)))
        else:
            return Response('values and annotates fields must be specified', status.HTTP_404_NOT_FOUND)


class ActivityList(ListAPIView):
    """
    Returns a list of IATI Activities stored in OIPA.

    ## Request parameters

    - `recipient_countries` (*optional*): Recipient countries list.
        Comma separated list of strings.
    - `recipient_regions` (*optional*): Recipient regions list.
        Comma separated list of integers.
    - `sectors` (*optional*): Sectors list. Comma separated list of integers.
    - `reporting_organisations` (*optional*): Organisation ID's list.
    - `participating_organisations` (*optional*): Organisation IDs list.
        Comma separated list of strings.
    - `min_total_budget` (*optional*): Minimal total budget value.
    - `max_total_budget` (*optional*): Maximal total budget value.
    - `aggregations` (*optional*): Aggregate available information.
        See [Available aggregations]() section for details.
    - `q` (*optional*): Search specific value in activities list.
        See [Searching]() section for details.
    - `fields` (*optional*): List of fields to display

    ## Available aggregations

    API request may include `aggregations` parameter.
    This parameter controls result aggregations and
    can be one or more (comma separated values) of:

    - `total_budget`: Calculate total budget of activities
        presented in filtered activities list.
    - `disbursement`: Calculate total disbursement of activities presented in
        filtered activities list.
    - `commitment`: Calculate total commitment of activities presented in
        filtered activities list.

    ## Searching

    API request may include `q` parameter. This parameter controls searching
    and contains expected value.

    Searching is performed on fields:

    - `id`
    - `title`
    - `total_budget`

    ## Result details

    Each result item contains short information about activity
    including URI to activity details.

    URI is constructed as follows: `/api/activities/{activity_id}`

    """
    queryset = Activity.objects.all()
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter,)
    filter_class = filters.ActivityFilter
    serializer_class = serializers.ActivitySerializer
    fields = ('url', 'id', 'title', 'total_budget')
    pagination_class = AggregationsPaginationSerializer

    # def get_serializer_context(self):
    #     return {'request': self.request }

    # def get_queryset(self):
    #     pk = self.kwargs.get('pk')
    #     return Activity.objects.prefetch_related('current_activity')


class ActivityDetail(RetrieveAPIView):
    """
    Returns detailed information about Activity.

    ## URI Format

    ```
    /api/activities/{activity_id}
    ```

    ### URI Parameters

    - `activity_id`: Desired activity ID

    ## Extra endpoints

    Detailed information about activity sectors, participating organizations
    and recipient countries can be found in separate pages:

    - `/api/activities/{activity_id}/sectors`: Lists sectors activity presents
    - `/api/activities/{activity_id}/participating-orgs`: List of participating
        organizations in this activity
    - `/api/activities/{activity_id}/recipient-countries`:
        List of recipient countries.

    ## Request parameters

    - `fields` (*optional*): List of fields to display

    """
    queryset = Activity.objects.all()
    serializer_class = serializers.ActivitySerializer


class ActivitySectors(ListAPIView):
    """
    Returns a list of IATI Activity Sectors stored in OIPA.

    ## URI Format

    ```
    /api/activities/{activity_id}/sectors
    ```

    ### URI Parameters

    - `activity_id`: Desired activity ID

    ## Result details

    Each result item contains:

    - `sector`: Sector name
    - `percentage`: The percentage of total commitments or total
        activity budget to this activity sector.
    - `vocabulary`: An IATI code for the vocabulary (see codelist) used
        for sector classifications.

    """
    serializer_class = serializers.ActivitySectorSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Activity(pk=pk).activitysector_set.all()


class ActivityParticipatingOrganisations(ListAPIView):
    """
    Returns a list of IATI Activity Participating Organizations stored in OIPA.

    ## URI Format

    ```
    /api/activities/{activity_id}/participating-orgs
    ```

    ### URI Parameters

    - `activity_id`: Desired activity ID

    """
    serializer_class = serializers.ParticipatingOrganisationSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Activity(pk=pk).participating_organisations.all()


class ActivityRecipientCountries(ListAPIView):
    """
    Returns a list of IATI Activity Recipient Countries stored in OIPA.

    ## URI Format

    ```
    /api/activities/{activity_id}/recipient-countries
    ```

    ### URI Parameters

    - `activity_id`: Desired activity ID

    """
    serializer_class = serializers.RecipientCountrySerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Activity(pk=pk).activityrecipientcountry_set.all()


class ActivityRecipientRegions(ListAPIView):
    """
    Returns a list of IATI Activity Recipient Regions stored in OIPA.

    ## URI Format

    ```
    /api/activities/{activity_id}/recipient-regions
    ```

    ### URI Parameters

    - `activity_id`: Desired activity ID

    """
    serializer_class = serializers.ActivityRecipientRegionSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Activity(pk=pk).activityrecipientregion_set.all()


class ActivityTransactions(ListAPIView):
    """
    Returns a list of IATI Activity Transactions stored in OIPA.

    ## URI Format

    ```
    /api/activities/{activity_id}/transactions
    ```

    ### URI Parameters

    - `activity_id`: Desired activity ID

    ## Request parameters:

    - `id` (*optional*): Transaction identifier
    - `aid_type` (*optional*): Aid type identifier
    - `activity__id` (*optional*): Activity id
    - `transaction_type` (*optional*): Transaction type identifier
    - `value` (*optional*): Transaction value.
    - `min_value` (*optional*): Minimal transaction value
    - `max_value` (*optional*): Maximal transaction value
    - `fields` (*optional*): List of fields to display

    ## Searching is performed on fields:

    - `description`
    - `provider_organisation_name`
    - `receiver_organisation_name`

    """
    serializer_class = TransactionSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Activity(pk=pk).transaction_set.all()
