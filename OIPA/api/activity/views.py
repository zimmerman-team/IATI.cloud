from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import authentication, mixins, status
from rest_framework.generics import (
    GenericAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from api.activity.filters import (
    ActivityAggregationFilter, ActivityFilter, RelatedOrderingFilter
)
from api.activity.serializers import (
    ActivityDateSerializer, ActivityPolicyMarkerSerializer,
    ActivityRecipientRegionSerializer, ActivitySectorSerializer,
    ActivitySerializer, ActivitySerializerByIatiIdentifier,
    BudgetItemSerializer, BudgetSerializer, CodelistSerializer,
    ConditionSerializer, ConditionsSerializer, ContactInfoSerializer,
    CountryBudgetItemsSerializer, CrsAddOtherFlagsSerializer, CrsAddSerializer,
    DescriptionSerializer, DocumentLinkCategorySerializer,
    DocumentLinkLanguageSerializer, DocumentLinkSerializer,
    FssForecastSerializer, FssSerializer, HumanitarianScopeSerializer,
    LegacyDataSerializer, LocationSerializer, OtherIdentifierSerializer,
    ParticipatingOrganisationSerializer, PlannedDisbursementSerializer,
    RecipientCountrySerializer, RelatedActivitySerializer,
    ReportingOrganisationSerializer,
    ResultIndicatorPeriodActualDimensionSerializer,
    ResultIndicatorPeriodActualLocationSerializer,
    ResultIndicatorPeriodSerializer,
    ResultIndicatorPeriodTargetDimensionSerializer,
    ResultIndicatorPeriodTargetLocationSerializer,
    ResultIndicatorReferenceSerializer, ResultIndicatorSerializer,
    ResultSerializer
)
from api.activity.validators import activity_required_fields
from api.aggregation.views import Aggregation, AggregationView, GroupBy
from api.cache import QueryParamsKeyConstructor
from api.country.serializers import CountrySerializer
from api.generics.filters import DistanceFilter, SearchFilter
from api.generics.views import (
    DynamicDetailCRUDView, DynamicDetailView, DynamicListCRUDView,
    DynamicListView, SaveAllSerializer
)
from api.organisation.serializers import OrganisationSerializer
from api.publisher.permissions import PublisherPermissions
from api.region.serializers import RegionSerializer
from api.sector.serializers import SectorSerializer
from api.transaction.filters import TransactionFilter
from api.transaction.serializers import TransactionSerializer
from geodata.models import Country, Region
from iati.activity_search_indexes import reindex_activity
from iati.models import (
    Activity, ActivityDate, ActivityParticipatingOrganisation,
    ActivityPolicyMarker, ActivityRecipientCountry, ActivityRecipientRegion,
    ActivityReportingOrganisation, ActivitySector, ActivityStatus, Budget,
    BudgetItem, CollaborationType, Condition, Conditions, ContactInfo,
    CountryBudgetItem, CrsAdd, CrsAddOtherFlags, Description, DocumentCategory,
    DocumentLink, DocumentLinkCategory, DocumentLinkLanguage, Fss, FssForecast,
    HumanitarianScope, LegacyData, Location, Organisation, OrganisationType,
    OtherIdentifier, PlannedDisbursement, PolicySignificance, RelatedActivity,
    Result, ResultIndicator, ResultIndicatorPeriod,
    ResultIndicatorPeriodActualDimension, ResultIndicatorPeriodTargetDimension,
    ResultIndicatorReference, Sector
)
from iati.transaction.models import Transaction
from iati_codelists.models import FileFormat, TransactionType


class FilterPublisherMixin(object):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        publisher_id = self.kwargs.get('publisher_id')

        return Activity.objects.filter(publisher__id=publisher_id)


class UpdateActivitySearchMixin(object):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def reindex_activity(self, serializer):
        instance = serializer.instance.get_activity()
        reindex_activity(instance)

    def perform_create(self, serializer):
        serializer.save()
        self.reindex_activity(serializer)

    def perform_update(self, serializer):
        serializer.save()
        self.reindex_activity(serializer)


class ActivityAggregations(AggregationView):
    """
    Returns aggregations based on the item grouped by,
    and the selected aggregation.

    ## Group by options

    API request has to include `group_by` parameter.

    This parameter controls result aggregations and
    can be one or more (comma separated values) of:

    - `recipient_country`
    - `recipient_region`
    - `sector`
    - `related_activity`
    - `reporting_organisation`
    - `participating_organisation`
    - `participating_organisation_type`
    - `document_link_category`
    - `activity_status`
    - `collaboration_type`

    ## Aggregation options

    API request has to include `aggregations` parameter.

    This parameter controls result aggregations and
    can be one or more (comma separated values) of:

    - `count`
    - `count_distinct`

    ## Request parameters

    All filters available on the Activity List, can be used on aggregations.

    """

    queryset = Activity.objects.all()

    filter_backends = (SearchFilter, DjangoFilterBackend,)
    filter_class = ActivityAggregationFilter

    allowed_aggregations = (
        Aggregation(
            query_param='count',
            field='count',
            annotate=Count('id'),
        ),
        Aggregation(
            query_param='count_distinct',
            field='count',
            annotate=Count('id', distinct=True),
        ),
    )

    allowed_groupings = (
        GroupBy(
            query_param="recipient_country",
            fields="recipient_country",
            queryset=Country.objects.all(),
            serializer=CountrySerializer,
            serializer_fields=('url', 'code', 'name', 'location', 'region'),
            name_search_field='recipient_country__name',
            renamed_name_search_field='recipient_country_name',
        ),
        GroupBy(
            query_param="recipient_region",
            fields="recipient_region",
            queryset=Region.objects.all(),
            serializer=RegionSerializer,
            serializer_fields=('url', 'code', 'name', 'location'),
            name_search_field="recipient_region__name",
            renamed_name_search_field="recipient_region_name",
        ),
        GroupBy(
            query_param="sector",
            fields="sector",
            queryset=Sector.objects.all(),
            serializer=SectorSerializer,
            serializer_fields=('url', 'code', 'name', 'location'),
            name_search_field="sector__name",
            renamed_name_search_field="sector_name",
        ),
        GroupBy(
            query_param="related_activity",
            fields=("relatedactivity__ref_activity__iati_identifier"),
            renamed_fields="related_activity",
        ),
        GroupBy(
            query_param="reporting_organisation",
            fields="reporting_organisations__organisation__id",
            renamed_fields="reporting_organisation",
            queryset=Organisation.objects.all(),
            serializer=OrganisationSerializer,
            serializer_main_field='id',
            name_search_field="reporting_organisations__organisation__primary_name",  # NOQA: E501
            renamed_name_search_field="reporting_organisation_name"
        ),
        GroupBy(
            query_param="participating_organisation",
            fields=("participating_organisations__primary_name",
                    "participating_organisations__normalized_ref"),
            renamed_fields=("participating_organisation",
                            "participating_organisation_ref"),
            queryset=ActivityParticipatingOrganisation.objects.all(),
            name_search_field="participating_organisations__primary_name",
            renamed_name_search_field="participating_organisation_name"
        ),
        GroupBy(
            query_param="participating_organisation_type",
            fields="participating_organisations__type",
            renamed_fields="participating_organisation_type",
            queryset=OrganisationType.objects.all(),
            serializer=CodelistSerializer,
            name_search_field="participating_organisations__type__name",
            renamed_name_search_field="participating_organisations_type_name"
        ),
        GroupBy(
            query_param="document_link_category",
            fields="documentlink__categories__code",
            renamed_fields="document_link_category",
            queryset=DocumentCategory.objects.all(),
            serializer=CodelistSerializer,
            name_search_field="documentlink__categories__name",
            renamed_name_search_field="document_link_category_name"
        ),
        GroupBy(
            query_param="document_link_file_format",
            fields="documentlink__file_format",
            renamed_fields="document_link_file_format",
            queryset=FileFormat.objects.all(),
            serializer=CodelistSerializer,
            name_search_field="documentlink__file_format__name",
            renamed_name_search_field="document_link_file_format"
        ),
        GroupBy(
            query_param="activity_status",
            fields="activity_status",
            queryset=ActivityStatus.objects.all(),
            serializer=CodelistSerializer,
            name_search_field="activity_status__name",
            renamed_name_search_field="activity_status_name"
        ),
        GroupBy(
            query_param="collaboration_type",
            fields="collaboration_type",
            renamed_fields="collaboration_type",
            queryset=CollaborationType.objects.all(),
            serializer=CodelistSerializer,
            name_search_field="collaboration_type__name",
            renamed_name_search_field="collaboration_type_name"
        ),
        GroupBy(
            query_param="policy_marker_significance",
            fields="activitypolicymarker__significance",
            renamed_fields="significance",
            queryset=PolicySignificance.objects.all(),
            serializer=CodelistSerializer,
        ),
    )


class ActivityList(CacheResponseMixin, DynamicListView):

    """
    Returns a list of IATI Activities stored in OIPA.

    ## Request parameters
    - `activity_id` (*optional*): Comma separated list of activity id's.
    - `activity_scope` (*optional*): Comma separated list of iso2 country codes.
    - `recipient_country` (*optional*): Comma separated list of iso2 country codes.
    - `recipient_region` (*optional*): Comma separated list of region codes.
    - `sector` (*optional*): Comma separated list of 5-digit sector codes.
    - `sector_category` (*optional*): Comma separated list of 3-digit sector codes.
    - `reporting_organisation_identifier` (*optional*): Comma separated list of reporting organisation IATI identifiers.
    - `participating_organisation` (*optional*): Comma separated list of organisation id's.
    - `total_budget_value_lte` (*optional*): Less then or equal total budget value
    - `total_budget_value_gte` (*optional*): Greater then or equal total budget value
    - `total_child_budget_value_lte` (*optional*): Less then or equal total child budget value
    - `total_child_budget_value_gte` (*optional*): Greater then or equal total child budget value
    - `planned_start_date_lte` (*optional*): Date in YYYY-MM-DD format, returns activities earlier or equal to the given activity date.
    - `planned_start_date_gte` (*optional*): Date in YYYY-MM-DD format, returns activities later or equal to the given activity date.
    - `actual_start_date_lte` (*optional*): Date in YYYY-MM-DD format, returns activities earlier or equal to the given activity date.
    - `actual_start_date_gte` (*optional*): Date in YYYY-MM-DD format, returns activities later or equal to the given activity date.
    - `planned_end_date_lte` (*optional*): Date in YYYY-MM-DD format, returns activities earlier or equal to the given activity date.
    - `planned_end_date_gte` (*optional*): Date in YYYY-MM-DD format, returns activities later or equal to the given activity date.
    - `actual_end_date_lte` (*optional*): Date in YYYY-MM-DD format, returns activities earlier or equal to the given activity date.
    - `actual_end_date_gte` (*optional*): Date in YYYY-MM-DD format, returns activities later or equal to the given activity date.
    - `activity_status` (*optional*): Comma separated list of activity statuses.
    - `hierarchy` (*optional*): Comma separated list of activity hierarchies.
    - `related_activity_id` (*optional*): Comma separated list of activity ids. Returns a list of all activities mentioning these activity id's.
    - `related_activity_type` (*optional*): Comma separated list of RelatedActivityType codes.
    - `related_activity_recipient_country` (*optional*): Comma separated list of iso2 country codes.
    - `related_activity_recipient_region` (*optional*): Comma separated list of region codes.
    - `related_activity_sector` (*optional*): Comma separated list of 5-digit sector codes.
    - `related_activity_sector_category` (*optional*): Comma separated list of 3-digit sector codes.
    - `transaction_provider_activity` (*optional*): Comma separated list of activity id's.
    - `transaction_date_year` (*optional*): Comma separated list of years in which the activity should have transactions.

    ## Text search

    API request may include `q` parameter. This parameter controls text search
    and contains expected value.

    By default, searching is performed on:

    - `iati_identifier` the IATI identifier
    - `title` narratives
    - `description` narratives
    - `recipient_country` recipient country code and name
    - `recipient_region` recipient region code and name
    - `reporting_org` ref and narratives
    - `sector` sector code and name
    - `document_link` url, category and title narratives
    - `participating_org` ref and narratives
    - `other_identifier` owner ref and narratives
    - `contact_info` all narratives for organisation, department, person name, job title & mailing address
    - `location` ref of location
    - `country_budget_items` narrative of budget item description
    - `policy_marker` narratives of policy marker
    - `transaction` ref and narratives of description, provider organisation, receiver organisation
    - `related_activity` ref of related activity
    - `conditions` narratives of condition
    - `result` narratives for result title, result description, result indicator title, result indicator description, result indicator period target comment, result indicator perioda ctual comment

    To search on subset of these fields the `q_fields` parameter can be used, like so;
    `q_fields=iati_identifier,title,description`

    ## Ordering

    API request may include `ordering` parameter. This parameter controls the order in which
    results are returned.

    Results can be ordered by:

    - `title`
    - `planned_start_date`
    - `actual_start_date`
    - `planned_end_date`
    - `actual_end_date`
    - `start_date`
    - `end_date`
    - `activity_budget_value`
    - `activity_incoming_funds_value`
    - `activity_disbursement_value`
    - `activity_expenditure_value`
    - `activity_plus_child_budget_value`

    The user may also specify reverse orderings by prefixing the field name with '-', like so: `-title`

    ## Aggregations

    At the moment there's no direct aggregations on this endpoint.

    The /activities/aggregations endpoint can be used for activity based aggregations.

    ## Result details

    Each item contains summarized information on the activity being shown,
    including the URI to activity details, which contain all information.
    To show more information in list view the `fields` parameter can be used. Example;
    `fields=activity_id,title,country,any_field`.

    """  # NOQA: E501

    queryset = Activity.objects.all()
    filter_backends = (
        SearchFilter,
        DjangoFilterBackend,
        DistanceFilter,
        RelatedOrderingFilter,
    )
    filter_class = ActivityFilter
    serializer_class = ActivitySerializer

    # make sure we can always have info about selectable fields,
    # stored into dict. This dict is populated in the DynamicView class using
    # _get_query_fields methods.
    selectable_fields = ()

    # Required fields for the serialisation defined by the
    # specification document
    fields = (
        'iati_identifier',
        'sectors',
        'recipient_regions',
        'recipient_countries',
        )
    # column headers with paths to the json property value.
    # reference to the field name made by the first term in the path
    # example: for recipient_countries.country.code path
    # reference field name is first term, meaning recipient_countries.
    csv_headers = \
        {
                   'iati_identifier': {'header': 'activity_id'},
                   'sectors.sector.code': {'header': 'sector_code'},
                   'sectors.percentage':  {'header': 'sectors_percentage'},
                   'recipient_countries.country.code': {'header': 'country'},
                   'recipient_regions.region.code': {'header': 'region'},
                   #'transaction_types': {'header': 'transaction_types'},
                   #'title.narratives.text': {'header': 'title'},
                   # 'descriptions.narratives.text':  {'header': 'description'},
                   # 'transaction_types.dsum': {'header': 'transaction_types'},
                   # 'reporting_organisation.type.code': {'header': 'reporting_organisation'}
        }
    # Get all transaction type
    transaction_types = []
    # Activity break down column
    break_down_by = 'sectors'
    # selectable fields which required different render logic.
    # Instead merging values using the delimiter, this fields will generate
    # additional columns for the different values, based on defined criteria.
    exceptional_fields = [{'transaction_types': transaction_types}]  # NOQA: E501

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
        'activity_budget_value',
        'activity_incoming_funds_value',
        'activity_disbursement_value',
        'activity_expenditure_value',
        'activity_plus_child_budget_value')

    list_cache_key_func = QueryParamsKeyConstructor()

    def __init__(self, *args, **kwargs):
        super(ActivityList, self).__init__(*args, **kwargs)

        for transaction_type in list(TransactionType.objects.all()):
            self.transaction_types.append(transaction_type.code)


class ActivityMarkReadyToPublish(APIView, FilterPublisherMixin):

    authentication_classes = (authentication.TokenAuthentication,)

    def post(self, request, publisher_id, pk):
        activity = Activity.objects.get(pk=pk)

        if (activity.ready_to_publish):
            activity.ready_to_publish = False
            activity.modified = True
            activity.save()
            return Response(False)

        # TODO: check if activity is valid for publishing- 2017-01-24
        if not activity_required_fields(activity):
            return Response({
                'error': True,
                'content': 'Not all required fields are on the activity'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        activity.ready_to_publish = True
        activity.modified = True
        activity.save()

        return Response(True)


class ActivityDetail(CacheResponseMixin, DynamicDetailView):

    """
    Returns detailed information about Activity.

    ## URI Format

    ```
    /api/activities/{activity_id}
    ```

    ### URI Parameters

    - `activity_id`: Desired activity ID

    ## Extra endpoints

    All information on activity transactions can be found on a separate page:

    - `/api/activities/{activity_id}/transactions/`:
        List of transactions.
    - `/api/activities/{activity_id}/provider-activity-tree/`:
        The upward and downward provider-activity-id traceability tree of this
        activity.

    ## Request parameters

    - `fields` (*optional*): List of fields to display

    """

    queryset = Activity.objects.all()
    filter_class = ActivityFilter
    serializer_class = ActivitySerializer

    # specification document
    fields = (
        'iati_identifier',
        'sectors',
        'recipient_regions',
        'recipient_countries',
        )

    # column headers with paths to the json property value.
    # reference to the field name made by the first term in the path
    # example: for recipient_countries.country.code path
    # reference field name is first term, meaning recipient_countries.
    csv_headers = \
        {
                   'iati_identifier': {'header': 'activity_id'},
                   'sectors.sector.code': {'header': 'sector_code'},
                   'sectors.percentage':  {'header': 'sectors_percentage'},
                   'recipient_countries.country.code': {'header': 'country'},
                   'recipient_regions.region.code': {'header': 'region'},
        }

    # Activity break down column
    break_down_by = 'sectors'

    exceptional_fields = [{'transaction_types': []}]  # NOQA: E501

# TODO separate endpoints for expensive fields like ActivityLocations &
# ActivityResults 08-07-2016


class ActivityDetailByIatiIdentifier(CacheResponseMixin, DynamicDetailView):
    """
    Returns detailed information of the Activity.

    ## URI Format

    ```
    /api/activities/{iati_identifier}
    ```

    ### URI Parameters

    - `iati_ideantifier`: Desired to IATI Identifier of activity

    ## Request parameters

    - `fields` (*optional*): List of fields to display

    """

    queryset = Activity.objects.all()
    filter_class = ActivityFilter
    serializer_class = ActivitySerializerByIatiIdentifier
    lookup_field = 'iati_identifier'


class ActivityTransactionList(DynamicListView):
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

    """  # NOQA: E501
    serializer_class = TransactionSerializer
    filter_class = TransactionFilter

    # TODO: Create cached logic for this class
    """
    This class has unique URL so not compatible the rest_framework_extensions
    cached. We should make a Params Key Constructor function
    then override the default below function and will be like below:

    @cache_response(key_func=YourQueryParamsKeyConstructor())
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    """

    def get_queryset(self):
        # Override default get query to get transaction list by primary key of
        # the activity
        pk = self.kwargs.get('pk')
        try:
            return Activity.objects.get(pk=pk).\
                transaction_set.all().order_by('id')
        except Activity.DoesNotExist:
            return Transaction.objects.none().order_by('id')


class ActivityTransactionListByIatiIdentifier(DynamicListView):
    """
    Returns a list of IATI Activity Transactions stored in OIPA.

    ## URI Format

    ```
    /api/activities/{iati_identifier}/transactions
    ```

    ### URI Parameters

    - `iati_identifier`: Desired activity IATI identifier

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

    """  # NOQA: E501
    serializer_class = TransactionSerializer
    filter_class = TransactionFilter

    # TODO: Create cached logic for this class
    """
    This class has unique URL so not compatible the rest_framework_extensions
    cached. We should make a Params Key Constructor function
    then override the default below function and will be like below:

    @cache_response(key_func=YourQueryParamsKeyConstructor())
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    """

    def get_queryset(self):
        # Override default get query to get transaction list by primary key of
        # the activity
        iati_identifier = self.kwargs.get('iati_identifier')
        try:
            return Activity.objects.get(iati_identifier=iati_identifier).\
                transaction_set.all().order_by('id')
        except Activity.DoesNotExist:
            return Transaction.objects.none().order_by('id')


class ActivityTransactionDetail(CacheResponseMixin, DynamicDetailView):
    serializer_class = TransactionSerializer

    def get_object(self):
        pk = self.kwargs.get('id')
        return Transaction.objects.get(pk=pk)


class ActivityListCRUD(UpdateActivitySearchMixin, FilterPublisherMixin,
                       DynamicListCRUDView):

    queryset = Activity.objects.all()
    filter_backends = (
        SearchFilter,
        DjangoFilterBackend,
        DistanceFilter,
        RelatedOrderingFilter,
    )
    filter_class = ActivityFilter
    serializer_class = ActivitySerializer

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
        'activity_budget_value',
        'activity_incoming_funds_value',
        'activity_disbursement_value',
        'activity_expenditure_value',
        'activity_plus_child_budget_value')


class ActivityDetailCRUD(UpdateActivitySearchMixin, DynamicDetailCRUDView):
    """
    Returns detailed information about Activity.

    ## URI Format

    ```
    /api/activities/{activity_id}
    ```

    ### URI Parameters

    - `activity_id`: Desired activity ID

    ## Extra endpoints

    All information on activity transactions can be found on a separate page:

    - `/api/activities/{activity_id}/transactions/`:
        List of transactions.
    - `/api/activities/{activity_id}/provider-activity-tree/`:
        The upward and downward provider-activity-id
        traceability tree of this activity.

    ## Request parameters

    - `fields` (*optional*): List of fields to display

    """
    queryset = Activity.objects.all()
    filter_class = ActivityFilter
    serializer_class = ActivitySerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )


class ActivityTransactionListCRUD(ListCreateAPIView):
    serializer_class = TransactionSerializer
    filter_class = TransactionFilter

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        try:
            return Activity.objects.get(pk=pk).\
                transaction_set.all().order_by('id')
        except Activity.DoesNotExist:
            return None


class ActivityTransactionDetailCRUD(RetrieveUpdateDestroyAPIView):
    serializer_class = TransactionSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        return Transaction.objects.get(pk=pk)


class ActivityReportingOrganisationList(UpdateActivitySearchMixin,
                                        ListCreateAPIView):
    serializer_class = ReportingOrganisationSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        try:
            return Activity.objects.get(pk=pk).reporting_organisations.all()
        except Activity.DoesNotExist:
            return None


class ActivityReportingOrganisationDetail(UpdateActivitySearchMixin,
                                          RetrieveUpdateDestroyAPIView):
    serializer_class = ReportingOrganisationSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        return ActivityReportingOrganisation.objects.get(pk=pk)


class ActivityDescriptionList(UpdateActivitySearchMixin, ListCreateAPIView):
    serializer_class = DescriptionSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        try:
            return Activity.objects.get(pk=pk).description_set.all()
        except Activity.DoesNotExist:
            return None


class ActivityDescriptionDetail(UpdateActivitySearchMixin,
                                RetrieveUpdateDestroyAPIView):
    serializer_class = DescriptionSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        return Description.objects.get(pk=pk)


class ActivityParticipatingOrganisationList(UpdateActivitySearchMixin,
                                            ListCreateAPIView):
    serializer_class = ParticipatingOrganisationSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        try:
            return Activity.objects.get(pk=pk).\
                participating_organisations.all()
        except Activity.DoesNotExist:
            return None


class ActivityParticipatingOrganisationDetail(
        UpdateActivitySearchMixin, RetrieveUpdateDestroyAPIView):
    serializer_class = ParticipatingOrganisationSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        return ActivityParticipatingOrganisation.objects.get(pk=pk)


class ActivityOtherIdentifierList(ListCreateAPIView):
    serializer_class = OtherIdentifierSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        try:
            return Activity.objects.get(pk=pk).other_identifier_set.all()
        except Activity.DoesNotExist:
            return None


class ActivityOtherIdentifierDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = OtherIdentifierSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        return OtherIdentifier.objects.get(pk=pk)


class ActivityActivityDateList(ListCreateAPIView):
    serializer_class = ActivityDateSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        try:
            return Activity.objects.get(pk=pk).activity_date_set.all()
        except Activity.DoesNotExist:
            return None


class ActivityActivityDateDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = ActivityDateSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        return ActivityDate.objects.get(pk=pk)


class ActivityContactInfoList(ListCreateAPIView):
    serializer_class = ContactInfoSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        try:
            return Activity.objects.get(pk=pk).contact_info_set.all()
        except Activity.DoesNotExist:
            return None


class ActivityContactInfoDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = ContactInfoSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        return ContactInfo.objects.get(pk=pk)


class ActivityRecipientCountryList(UpdateActivitySearchMixin, ListCreateAPIView):  # NOQA: E501
    serializer_class = RecipientCountrySerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        try:
            return Activity.objects.get(pk=pk).\
                activityrecipientcountry_set.all()
        except Activity.DoesNotExist:
            return None


class ActivityRecipientCountryDetail(UpdateActivitySearchMixin,
                                     RetrieveUpdateDestroyAPIView):
    serializer_class = RecipientCountrySerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        return ActivityRecipientCountry.objects.get(pk=pk)


class ActivityRecipientRegionList(UpdateActivitySearchMixin, ListCreateAPIView):  # NOQA: E501
    serializer_class = ActivityRecipientRegionSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        try:
            return Activity.objects.get(pk=pk).\
                activityrecipientregion_set.all()
        except Activity.DoesNotExist:
            return None


class ActivityRecipientRegionDetail(UpdateActivitySearchMixin,
                                    RetrieveUpdateDestroyAPIView):
    serializer_class = ActivityRecipientRegionSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        return ActivityRecipientRegion.objects.get(pk=pk)


class ActivitySectorList(UpdateActivitySearchMixin, ListCreateAPIView):
    serializer_class = ActivitySectorSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        try:
            return Activity.objects.get(
                pk=pk
            ).activitysector_set.all()
        except Activity.DoesNotExist:
            return None


class ActivitySectorDetail(UpdateActivitySearchMixin,
                           RetrieveUpdateDestroyAPIView):
    serializer_class = ActivitySectorSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        return ActivitySector.objects.get(pk=pk)


class ActivityCountryBudgetItemDetail(mixins.RetrieveModelMixin,
                                      mixins.UpdateModelMixin,
                                      mixins.DestroyModelMixin,
                                      mixins.CreateModelMixin,
                                      GenericAPIView):
    serializer_class = CountryBudgetItemsSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('pk')
        return CountryBudgetItem.objects.get(activity=pk)


class ActivityBudgetItemList(ListCreateAPIView):
    serializer_class = BudgetItemSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        try:
            return Activity.objects.get(
                pk=pk).country_budget_items.budgetitem_set.all()
        except Activity.DoesNotExist:
            return None


class ActivityBudgetItemDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = BudgetItemSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('budget_item_id')
        return BudgetItem.objects.get(pk=pk)


class ActivityLocationList(ListCreateAPIView):
    serializer_class = LocationSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        try:
            return Activity.objects.get(pk=pk).locations.all()
        except Activity.DoesNotExist:
            return None


class ActivityLocationDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = LocationSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        return Location.objects.get(pk=pk)


class ActivityHumanitarianScopeList(ListCreateAPIView):
    serializer_class = HumanitarianScopeSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        try:
            return Activity.objects.get(pk=pk).\
                humanitarianscope_set.all()
        except Activity.DoesNotExist:
            return None


class ActivityHumanitarianScopeDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = HumanitarianScopeSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        return HumanitarianScope.objects.get(pk=pk)


class ActivityPolicyMarkerList(ListCreateAPIView):
    serializer_class = ActivityPolicyMarkerSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        try:
            return Activity.objects.get(pk=pk).\
                activitypolicymarker_set.all()
        except Activity.DoesNotExist:
            return None


class ActivityPolicyMarkerDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = ActivityPolicyMarkerSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        return ActivityPolicyMarker.objects.get(pk=pk)


class ActivityBudgetList(ListCreateAPIView):
    serializer_class = BudgetSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        try:
            return Activity.objects.get(pk=pk).budgets.all()
        except Activity.DoesNotExist:
            return None


class ActivityBudgetDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = BudgetSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        return Budget.objects.get(pk=pk)


class ActivityPlannedDisbursementList(ListCreateAPIView):
    serializer_class = PlannedDisbursementSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        try:
            return Activity.objects.get(pk=pk).\
                planned_disbursements.all()
        except Activity.DoesNotExist:
            return None


class ActivityPlannedDisbursementDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = PlannedDisbursementSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        return PlannedDisbursement.objects.get(pk=pk)


class ActivityDocumentLinkList(UpdateActivitySearchMixin, ListCreateAPIView):
    serializer_class = DocumentLinkSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        try:
            return Activity.objects.get(pk=pk).\
                documentlink_set.all()
        except Activity.DoesNotExist:
            return None


class ActivityDocumentLinkDetail(UpdateActivitySearchMixin,
                                 RetrieveUpdateDestroyAPIView):
    serializer_class = DocumentLinkSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        return DocumentLink.objects.get(pk=pk)


class ActivityDocumentLinkCategoryList(ListCreateAPIView):
    serializer_class = DocumentLinkCategorySerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('document_link_id')
        return DocumentLink(pk=pk).documentlinkcategory_set.all()


class ActivityDocumentLinkCategoryDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = DocumentLinkCategorySerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('category_id')
        return DocumentLinkCategory.objects.get(pk=pk)


class ActivityDocumentLinkLanguageList(ListCreateAPIView):
    serializer_class = DocumentLinkLanguageSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('document_link_id')
        return DocumentLink(pk=pk).documentlinklanguage_set.all()


class ActivityDocumentLinkLanguageDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = DocumentLinkLanguageSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('language_id')
        return DocumentLinkLanguage.objects.get(pk=pk)


class ActivityRelatedActivityList(ListCreateAPIView):
    serializer_class = RelatedActivitySerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        try:
            return Activity.objects.get(pk=pk).\
                related_activities.all()
        except Activity.DoesNotExist:
            return None


class ActivityRelatedActivityDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = RelatedActivitySerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        try:
            return RelatedActivity.objects.get(pk=pk)
        except Activity.DoesNotExist:
            return None


class ActivityLegacyDataList(ListCreateAPIView):
    serializer_class = LegacyDataSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        try:
            return Activity.objects.get(pk=pk).legacydata_set.all()
        except Activity.DoesNotExist:
            return None


class ActivityLegacyDataDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = LegacyDataSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        return LegacyData.objects.get(pk=pk)


class ActivityResultList(ListCreateAPIView):
    serializer_class = ResultSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        try:
            return Activity.objects.get(pk=pk).results.all()
        except Activity.DoesNotExist:
            return None


class ActivityResultDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = ResultSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        return Result.objects.get(pk=pk)


class ResultIndicatorList(ListCreateAPIView):
    serializer_class = ResultIndicatorSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('activity_id')
        try:
            return Activity.objects.get(pk=pk).\
                result_indicators.all()
        except Activity.DoesNotExist:
            return None


class ResultIndicatorDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = ResultIndicatorSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('resultindicator_id')
        return ResultIndicator.objects.get(pk=pk)


class ResultIndicatorReferenceList(ListCreateAPIView):
    serializer_class = ResultIndicatorReferenceSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('resultindicator_id')
        try:
            return Activity.objects.get(pk=pk).\
                result_indicator_references.all()
        except Activity.DoesNotExist:
            return None


class ResultIndicatorReferenceDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = ResultIndicatorReferenceSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('reference_id')
        return ResultIndicatorReference.objects.get(pk=pk)


class ResultIndicatorPeriodList(ListCreateAPIView):
    serializer_class = ResultIndicatorPeriodSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('resultindicator_id')
        try:
            return Activity.objects.get(pk=pk).\
                result_indicator_periods.all()
        except Activity.DoesNotExist:
            return None


class ResultIndicatorPeriodDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = ResultIndicatorPeriodSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('period_id')
        return ResultIndicatorPeriod.objects.get(pk=pk)


class ResultIndicatorPeriodActualLocationList(ListCreateAPIView):
    serializer_class = \
        ResultIndicatorPeriodActualLocationSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('resultindicator_id')
        try:
            return Activity.objects.get(
                pk=pk).result_indicator_period_actual_locations.all()
        except Activity.DoesNotExist:
            return None


class ResultIndicatorPeriodTargetLocationList(ListCreateAPIView):
    serializer_class = \
        ResultIndicatorPeriodTargetLocationSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('resultindicator_id')
        try:
            return Activity.objects.get(
                pk=pk).result_indicator_period_target_locations.all()
        except Activity.DoesNotExist:
            return None


class ResultIndicatorPeriodActualDimensionList(ListCreateAPIView):
    serializer_class = \
        ResultIndicatorPeriodActualDimensionSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('resultindicator_id')
        try:
            return Activity.objects.get(
                pk=pk).result_indicator_period_actual_dimensions.all()
        except Activity.DoesNotExist:
            return None


class ResultIndicatorPeriodActualDimensionDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = \
        ResultIndicatorPeriodActualDimensionSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('actual_dimension_id')
        return \
            ResultIndicatorPeriodActualDimension.objects.get(pk=pk)


class ResultIndicatorPeriodTargetDimensionList(ListCreateAPIView):
    serializer_class = \
        ResultIndicatorPeriodTargetDimensionSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('resultindicator_id')
        try:
            return Activity.objects.get(
                pk=pk).result_indicator_period_target_dimensions.all()
        except Activity.DoesNotExist:
            return None


class ResultIndicatorPeriodTargetDimensionDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = \
        ResultIndicatorPeriodTargetDimensionSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('target_dimension_id')
        return \
            ResultIndicatorPeriodTargetDimension.objects.get(pk=pk)


class ActivityConditionsDetail(SaveAllSerializer):
    serializer_class = ConditionsSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('pk')
        return Conditions.objects.get(activity=pk)


class ActivityConditionList(ListCreateAPIView):
    serializer_class = ConditionSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        try:
            return Activity.objects.get(pk=pk).conditions.\
                condition_set.all()
        except Activity.DoesNotExist:
            return None


class ActivityConditionDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = ConditionSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('condition_id')
        return Condition.objects.get(pk=pk)


class ActivityCrsAddList(ListCreateAPIView):
    serializer_class = CrsAddSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        try:
            return Activity.objects.get(pk=pk).crsadd_set.all()
        except Activity.DoesNotExist:
            return None


class ActivityCrsAddDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = CrsAddSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        return CrsAdd.objects.get(pk=pk)


class ActivityCrsAddOtherFlagsList(ListCreateAPIView):
    serializer_class = CrsAddOtherFlagsSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        try:
            return Activity.objects.get(pk=pk).crsadd_set.all()
        except Activity.DoesNotExist:
            return None


class ActivityCrsAddOtherFlagsDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = CrsAddOtherFlagsSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        return CrsAddOtherFlags.objects.get(pk=pk)


class ActivityFssList(ListCreateAPIView):
    serializer_class = FssSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        try:
            return Activity.objects.get(pk=pk).crsadd_set.all()
        except Activity.DoesNotExist:
            return None


class ActivityFssDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = FssSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('id')
        return Fss.objects.get(pk=pk)


class ActivityFssForecastList(ListCreateAPIView):
    serializer_class = FssForecastSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_queryset(self):
        pk = self.kwargs.get('id')
        return Fss(pk=pk).fssforecast_set.all()


class ActivityFssForecastDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = FssForecastSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (PublisherPermissions, )

    def get_object(self):
        pk = self.kwargs.get('forecast_id')
        return FssForecast.objects.get(pk=pk)
