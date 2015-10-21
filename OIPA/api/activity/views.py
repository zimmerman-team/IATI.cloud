from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.generics import GenericAPIView
from iati.models import Activity
from api.activity import serializers as activitySerializers
from api.activity import filters
from api.activity.aggregation import AggregationsPaginationSerializer
from api.activity.activity_aggregation import ActivityAggregationSerializer
from api.generics.filters import SearchFilter
from api.generics.views import DynamicListView, DynamicDetailView

from rest_framework.filters import DjangoFilterBackend

from api.transaction.serializers import TransactionSerializer
from api.transaction.filters import TransactionFilter

from rest_framework.response import Response
from rest_framework import mixins, status


class ActivityAggregations(GenericAPIView):
    """
    Returns aggregations based on the item grouped by, and the selected aggregation.

    ## Group by options

    API request has to include `group_by` parameter.
    This parameter controls result aggregations and
    can be one or more (comma separated values) of:

    - `recipient_country`
    - `recipient_region`
    - `sector`
    - `reporting_organisation`
    - `participating_organisation`
    - `activity_status`
    - `policy_marker`
    - `collaboration_type`
    - `default_flow_type`
    - `default_aid_type`
    - `default_finance_type`
    - `default_tied_status`
    - `budget_per_year`
    - `budget_per_quarter`

    ## Aggregation options

    API request has to include `aggregations` parameter.
    This parameter controls result aggregations and
    can be one or more (comma separated values) of:

    - `count`
    - `budget`
    - `disbursement`
    - `expenditure`
    - `commitment`
    - `incoming_fund`


    ## Request parameters

    All filters available on the Activity List, can be used on aggregations.

    """

    queryset = Activity.objects.all()

    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter,)
    filter_class = filters.ActivityFilter

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        results = ActivityAggregationSerializer(
            queryset,
            context=self.get_serializer_context())

        if results.data:
            if isinstance(results.data, dict) and results.data.get('error_message'):
                return Response(results.data.get('error_message'))
            return Response(results.data)
        else:
            return Response('No results', status.HTTP_204_NO_CONTENT)


class ActivityList(DynamicListView):
    """
    Returns a list of IATI Activities stored in OIPA.

    ## Request parameters
    - `ids` (*optional*): Comma separated list of activity id's.
    - `activity_scope` (*optional*): Comma separated list of iso2 country codes.
    - `recipient_country` (*optional*): Comma separated list of iso2 country codes.
    - `recipient_region` (*optional*): Comma separated list of region codes.
    - `sector` (*optional*): Comma separated list of 5-digit sector codes.
    - `sector_category` (*optional*): Comma separated list of 3-digit sector codes.
    - `reporting_organisation` (*optional*): Comma separated list of organisation id's.
    - `participating_organisation` (*optional*): Comma separated list of organisation id's.
    - `min_total_budget` (*optional*): Minimal total budget value.
    - `max_total_budget` (*optional*): Maximal total budget value.
    - `start_date_actual_lte` (*optional*): Date in YYYY-MM-DD format, returns activities earlier or equal to the given date.
    - `start_date_actual_gte` (*optional*): Date in YYYY-MM-DD format, returns activities later or equal to the given date.
    - `activity_status` (*optional*): Comma separated list of activity statuses.
    - `hierarchy` (*optional*): Comma separated list of activity hierarchies.
    - `related_activity_id` (*optional*): Comma separated list of activity ids. Returns a list of all activities mentioning these activity id's.
    - `related_activity_type` (*optional*): Comma separated list of RelatedActivityType codes.
    - `related_activity_recipient_country` (*optional*): Comma separated list of iso2 country codes.
    - `related_activity_recipient_region` (*optional*): Comma separated list of region codes.
    - `related_activity_sector` (*optional*): Comma separated list of 5-digit sector codes.
    - `related_activity_sector_category` (*optional*): Comma separated list of 3-digit sector codes.
    - `transaction_provider_activity` (*optional*): Comma separated list of activity id's.


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

    For more advanced aggregations please use the /activities/aggregations endpoint.

    ## Searching

    API request may include `q` parameter. This parameter controls searching
    and contains expected value.

    By default, searching is performed on fields:

    - `id`
    - `title`
    - `total_budget`

    To search on  subset of these fields the `q_fields' parameter can be used. Example;
    `q_fields=activity_id,title,description'

    ## Result details

    Each item contains summarized information on the activity being shown,
    including the URI to activity details. To show more information, go to the
    activity's detail page or select any field using the `fields` parameter on the list. Example;
    `fields=activity_id,title,country,any_field`.

    """
    queryset = Activity.objects.all()
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter,)
    filter_class = filters.ActivityFilter
    serializer_class = activitySerializers.ActivitySerializer
    fields = ('url', 'iati_identifier', 'title', 'description', 'transactions', 'reporting_organisations')
    pagination_class = AggregationsPaginationSerializer

    # def get_serializer_context(self):
    #     return {'request': self.request }

    # def get_queryset(self):
    #     pk = self.kwargs.get('pk')
    #     return Activity.objects.prefetch_related('current_activity')


class ActivityDetail(DynamicDetailView):
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

#     def get_queryset(self):
#         # print('called')
#         # obj = super(ActivityDetail, self).get_queryset()
#         # print(obj0

#         from iati.models import ActivityParticipatingOrganisation, Narrative

#         pk = self.kwargs.get('pk')
#         # print(Narrative.objects.filter(iati_identifier=pk))

#         # narratives = Narrative.objects.filter(iati_identifier=pk).select_related('language')
#         # activities = Activity.objects.all().prefetch_related(narrative_prefetch)
#         narrative_qs = Narrative.objects.select_related('language')
#         narrative_prefetch = Prefetch('narratives', queryset=narrative_qs, to_attr='narrative_test')

#         obj_prefetch = Prefetch('narratives', queryset=narrative_qs)

#         # narratives = queryset=Narrative.objects.filter(iati_identifier=pk).select_related('language')
#         prefetch = Prefetch('participating_organisations',
#                 queryset=ActivityParticipatingOrganisation.objects.all().select_related('type', 'role', 'organisation').prefetch_related(obj_prefetch))

#         # a = list(Activity.objects.prefetch_related(narrative_prefetch).all())
#         # b = a[0].participating_organisations.all()[0]
#         # print(b)
#         # print(a[1]).narratives.filter(parent_object=)
#         return Activity.objects.all().prefetch_related(narrative_prefetch, prefetch)

#     # def get_queryset(self):
#     #     pk = self.kwargs.get('pk')
#     #     print(pk)
#     #     return Activity.objects.get(pk=pk)

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

    - `recipient_country` (*optional*): Recipient countries list.
        Comma separated list of strings.
    - `recipient_region` (*optional*): Recipient regions list.
        Comma separated list of integers.
    - `sector` (*optional*): Sectors list. Comma separated list of integers.
    - `sector_category` (*optional*): Sectors list. Comma separated list of integers.
    - `reporting_organisations` (*optional*): Organisation ID's list.
    - `participating_organisations` (*optional*): Organisation IDs list.
        Comma separated list of strings.
    - `min_total_budget` (*optional*): Minimal total budget value.
    - `max_total_budget` (*optional*): Maximal total budget value.
    - `activity_status` (*optional*):


    - `related_activity_id` (*optional*):
    - `related_activity_type` (*optional*):
    - `related_activity_recipient_country` (*optional*):
    - `related_activity_recipient_region` (*optional*):
    - `related_activity_sector` (*optional*):

    ## Searching is performed on fields:

    - `description`
    - `provider_organisation_name`
    - `receiver_organisation_name`

    """
    serializer_class = TransactionSerializer
    filter_class = TransactionFilter


    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Activity(pk=pk).transaction_set.all()
