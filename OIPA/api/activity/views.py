from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView, GenericAPIView
from rest_framework.serializers import BaseSerializer
from iati.models import Activity
from api.activity import serializers as activitySerializers
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

from geodata.models import Country, Region
from iati.models import Organisation, Sector, ActivityStatus, PolicyMarker, CollaborationType, FlowType, AidType, FinanceType, TiedStatus

from api.activity.serializers import ActivitySerializer, ActivityStatusSerializer, \
                                     ParticipatingOrganisationSerializer, PolicyMarkerSerializer, \
                                     CollaborationTypeSerializer, FlowTypeSerializer, AidTypeSerializer, FinanceTypeSerializer, TiedStatusSerializer
from api.country.serializers import CountrySerializer
from api.region.serializers import RegionSerializer
from api.sector.serializers import SectorSerializer
from api.organisation.serializers import OrganisationSerializer

class ActivityAggregationSerializer(BaseSerializer):

    _aggregations = {
        "count": {
            "field": "count",
            "annotate_name": "count",
            "annotate": Count('id')
        },
        "budget": {
            "field": "budget",
            "annotate_name": "budget",
            "annotate": Sum('budget__value')
        },
        "total_budget": {
            "field": "total_budget",
            "annotate_name": 'total_budget',
            "annotate": Sum('total_budget')
        },
        "disbursement": {
            "field": "disbursement",
            "extra_filter": Q(transaction__transaction_type='D'),
            "annotate_name": 'disbursement',
            "annotate": Sum('transaction__value'),
        },
        "expenditure": {
            "field": "expenditure",
            "extra_filter": Q(transaction__transaction_type='E'),
            "annotate_name": "expenditure",
            "annotate": Sum('transaction__value')
        },
        "commitment": {
            "field": "commitment",
            "extra_filter": Q(transaction__transaction_type='C'),
            "annotate_name": 'commitment',
            "annotate": Sum('transaction__value')
        },
        "incoming_fund": {
            "field": "incoming_fund",
            "extra_filter": Q(transaction__transaction_type='IF'),
            "annotate_name": 'incoming_fund',
            "annotate": Sum('transaction__value')
        },
    }

    _allowed_groupings = {
        "recipient_country": {
            "field": "recipient_country",
            "queryset": Country.objects.all(),
            "serializer": CountrySerializer,
            "fields": ('url', 'code', 'name'),
            # "subquery": "SELECT * FROM geodata_country WHERE geodata_country.code = recipient_country",
        },
        "recipient_region": {
            "field": "recipient_region",
            "queryset": Region.objects.all(),
            "serializer": RegionSerializer,
            "fields": ('url', 'code', 'name'),
        },
        "sector": {
            "field": "sector",
            "queryset": Sector.objects.all(),
            "serializer": SectorSerializer,
            "fields": ('url', 'code', 'name'),
        },
        "reporting_organisation": {
            "field": "reporting_organisation",
            "queryset": Organisation.objects.all(),
            "serializer": OrganisationSerializer,
            "fields": ('url', 'code', 'name'),
        },
        "participating_organisation": {
            "field": "participating_organisation",
            "queryset": Organisation.objects.all(),
            "serializer": ParticipatingOrganisationSerializer,
            "fields": ('url', 'code', 'name'),
        },
        "activity_status": {
            "field": "activity_status",
            "queryset": ActivityStatus.objects.all(),
            "serializer": ActivityStatusSerializer,
            "fields": (), # has default fields
        },
        "policy_marker": {
            "field": "policy_marker",
            "queryset": PolicyMarker.objects.all(),
            "serializer": PolicyMarkerSerializer,
            "fields": (), # has default fields
        },
        "collaboration_type": {
            "field": "collaboration_type",
            "queryset": CollaborationType.objects.all(),
            "serializer": CollaborationTypeSerializer,
            "fields": (), # has default fields
        },
        "default_flow_type": {
            "field": "default_flow_type",
            "queryset": FlowType.objects.all(),
            "serializer": FlowTypeSerializer,
            "fields": (), # has default fields
        },
        "default_aid_type": {
            "field": "default_aid_type",
            "queryset": AidType.objects.all(),
            "serializer": AidTypeSerializer,
            "fields": (), # has default fields
        },
        "collaboration_type": {
            "field": "default_finance_type",
            "queryset": FinanceType.objects.all(),
            "serializer": FinanceTypeSerializer,
            "fields": (), # has default fields
        },
        "default_tied_status": {
            "field": "default_tied_status",
            "queryset": TiedStatus.objects.all(),
            "serializer": TiedStatusSerializer,
            "fields": (), # has default fields
        },
    }

    _allowed_orderings = [ i['field'] for i in _allowed_groupings.values()]

    def apply_order_filters(self, queryset, orderList, groupList, aggregationList):
        # todo: limit order_by fields

        allowed_orderings = self._allowed_orderings + aggregationList
        orderings = self._intersection(allowed_orderings, orderList)

        print(orderings)

        if (len(orderings)):
            return queryset.order_by(*orderings)
        # else: 
        #     return queryset.order_by(*self._intersection(allowed_orderings, groupList))

        return queryset

    def apply_annotations(self, queryset, groupList, aggregationList):

        first_queryset = queryset
        first_annotations = dict()
        first_result = dict()
        result = dict()

        same_query_aggregations = [ i for i in aggregationList if not self._aggregations[i].get('extra_filter') ]
        separate_aggregations = [ i for i in aggregationList if self._aggregations[i].get('extra_filter') ]

        for aggregation in same_query_aggregations:
            a = self._aggregations.get(aggregation, {})
            first_annotations[a['annotate_name']] = a['annotate']
     
        # aggregations that can be performed in the same query (hence require no extra filters)
        result = first_queryset.values(*groupList).annotate(**first_annotations)

        # aggregations that require extra filters, and hence must be exectued separately
        for aggregation in separate_aggregations:
            # field = self._aggregations.get("")
            a = self._aggregations.get(aggregation, None)
            extra_filter = a["extra_filter"]
            field = a["field"]

            annotation = dict([(a['annotate_name'], a['annotate'])])
            next_result = queryset.filter(extra_filter).values(*groupList).annotate(**annotation)
            
            main_group_field = groupList[0]


            if len(next_result):
                # join results in results object (first_result >= new_result)
                iold = iter(result)
                inew = iter(next_result)

                n = next(inew)
                for o in iold: 

                    if (n[main_group_field] == o[main_group_field]):
                        o[field] = n[field]

                        try:
                            n = next(inew)
                        except StopIteration:
                            break

        return result

    def serialize_foreign_keys(self, valuesQuerySet, request, groupList):

        serializers = {}

        for grouping in groupList:
            field_name = self._allowed_groupings[grouping]["field"]
            serializer = self._allowed_groupings[grouping]["serializer"]
            fields = self._allowed_groupings[grouping]["fields"]
            foreignQueryset = self._allowed_groupings[grouping]["queryset"]

            if fields:
                data = serializer(foreignQueryset, 
                    context={
                        'request': request,
                    },
                    many=True,
                    fields=fields,
                    query_field="%s_fields" % (field_name),
                ).data
            else: 
                data = serializer(foreignQueryset, 
                    context={
                        'request': request,
                    },
                    many=True,
                ).data

            serializers[grouping] = { i.get('code'):i for i in data }

        results = valuesQuerySet

        for i, result in enumerate(results):
            for k,v in result.iteritems():
                if k in groupList:
                    # print(k)
                    print(serializers.get(k, {}))
                    result[k] = serializers.get(k, {}).get(str(v))

        return results

    def to_representation(self, queryset):
        request = self.context.get('request') 
        params = request.query_params

        order_by = filter(None, params.get('order_by', "").split(','))
        # order_by = self._union(filter(None, params.get('order_by', "").split(',')), self._allowed_groupings.keys())
        group_by = self._intersection(filter(None, params.get('group_by', "").split(',')), self._allowed_groupings.keys())
        aggregations = self._intersection(filter(None,params.get('aggregations', "").split(',')), self._aggregations.keys())

        if not (len(group_by) and len(aggregations)):
            return Response(
                'Provide both group_by and aggregations', 
                status.HTTP_404_NOT_FOUND,
            )


        # queryset = self.apply_group_filters(queryset, request, group_by)
        queryset = self.apply_order_filters(queryset, order_by, group_by, aggregations) 
        result = self.apply_annotations(queryset, group_by, aggregations)
        result = self.serialize_foreign_keys(result, request, group_by)

        return result

    def _union(self, list1, list2):
        return list(set(list1) | set(list2))

    def _intersection(self, list1, list2):
        return list(set(list1) & set(list2))


class ActivityAggregations(GenericAPIView):

    queryset = Activity.objects.all()

    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter,)
    filter_class = filters.ActivityFilter
    # serializer_class = activitySerializers.AggregationSerializer
    # fields = ('url', 'id', 'title', 'total_budget')
    # pagination_serializer_class = AggregationsPaginationSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        results = ActivityAggregationSerializer(queryset,
            context=self.get_serializer_context())

        if (results.data):
            return Response(results.data)
        else:
            return Response('No results', status.HTTP_404_NOT_FOUND)

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
    serializer_class = activitySerializers.ActivitySerializer
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
    serializer_class = activitySerializers.ActivitySerializer


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
    serializer_class = activitySerializers.ActivitySectorSerializer

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
    serializer_class = activitySerializers.ParticipatingOrganisationSerializer

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
    serializer_class = activitySerializers.RecipientCountrySerializer

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
    serializer_class = activitySerializers.ActivityRecipientRegionSerializer

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
