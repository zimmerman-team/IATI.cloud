from rest_framework.generics import ListAPIView
from rest_framework.filters import DjangoFilterBackend

from api.budget import filters
from api.generics.filters import SearchFilter

from api.aggregation.views import AggregationView, Aggregation, GroupBy

from django.db.models import Count, Sum, F

from geodata.models import Country
from geodata.models import Region
from iati.models import Activity
from iati.models import Budget
from iati.models import Sector
from iati.models import ActivityStatus
from iati.models import PolicyMarker
from iati.models import CollaborationType
from iati.models import DocumentCategory
from iati.models import FlowType
from iati.models import AidType
from iati.models import FinanceType
from iati.models import TiedStatus
from iati.models import ActivityParticipatingOrganisation
from iati.models import OrganisationType
from iati.models import Organisation

from api.activity.serializers import CodelistSerializer
from api.country.serializers import CountrySerializer
from api.region.serializers import RegionSerializer
from api.sector.serializers import SectorSerializer
from api.organisation.serializers import OrganisationSerializer


# These are the accepted currencies
currencies = [
    'xdr',
    'usd',
    'eur',
    'gbp',
    'jpy',
    'cad'
]

def annotate_currency(query_params, groupings):
    """
    Choose the right currency field, and aggregate differently based on group_by
    """
    currency = query_params.get('convert_to')
    currency_field = None
    
    if currency: 
        currency = currency.lower()

    if currency is None or currency not in currencies:
        currency_field = 'value'
    else:
        currency_field = currency + '_value'

    annotation_components = F(currency_field)

    param_additions = []

    for param in query_params:
        if param == 'sector':
            param_additions.append('budgetsector__percentage')

    grouping_additions = []

    for grouping in groupings:
        if grouping.query_param == 'sector':
            grouping_additions.append('budgetsector__percentage')

    additions = list(set(param_additions).union(grouping_additions))

    for percentage_field in additions:
        percentage_expression = F(percentage_field) / 100.0
        annotation_components = annotation_components * percentage_expression

    return Sum(annotation_components)



class BudgetAggregations(AggregationView):
    """
    Returns aggregations based on the item grouped by, and the selected aggregation.

    ## Group by options

    API request has to include `group_by` parameter.
    
    This parameter controls result aggregations and
    can be one or more (comma separated values) of:

    - `recipient_country` Non percentage weighted
    - `recipient_region` Non percentage weighted
    - `sector` Percentage weighted
    - `related_activity`
    - `reporting_organisation`
    - `participating_organisation`
    - `participating_organisation_type`
    - `document_link_category`
    - `activity_status`
    - `collaboration_type`
    - `budget_period_start_year`
    - `budget_period_end_year`
    - `budget_period_start_quarter`
    - `budget_period_end_quarter`
    - `budget_period_start_month`
    - `budget_period_end_month`

    ## Aggregation options

    API request has to include `aggregations` parameter.
    
    This parameter controls result aggregations and
    can be one or more (comma separated values) of:

    - `count` Count of budgets
    - `activity_count` Count of activities
    - `value` Sum of budget value (in the selected currency)

    ## Request parameters

    All filters available on the Activity List, can be used on aggregations.

    """

    queryset = Budget.objects.all()

    filter_backends = (SearchFilter, DjangoFilterBackend,)
    filter_class = filters.BudgetFilter

    allowed_aggregations = (
        Aggregation(
            query_param='count',
            field='count',
            annotate=Count('id'),
        ),
        Aggregation(
            query_param='activity_count',
            field='activity_count',
            annotate=Count('activity', distinct=True),
        ),
        Aggregation(
            query_param='value',
            field='value',
            annotate=annotate_currency,
        ),
    )

    allowed_groupings = (
        GroupBy(
            query_param="recipient_country",
            fields="activity__recipient_country",
            renamed_fields="recipient_country",
            queryset=Country.objects.all(),
            serializer=CountrySerializer,
            serializer_fields=('url', 'code', 'name', 'location'),
            name_search_field='activity__recipient_country__name',
            renamed_name_search_field='recipient_country_name',
        ),
        GroupBy(
            query_param="recipient_region",
            fields="activity__recipient_region",
            renamed_fields="recipient_region",
            queryset=Region.objects.all(),
            serializer=RegionSerializer,
            serializer_fields=('url', 'code', 'name', 'location'),
            name_search_field="activity__recipient_region__name",
            renamed_name_search_field="recipient_region_name",
        ),
        GroupBy(
            query_param="sector",
            fields="budgetsector__sector",
            renamed_fields="sector",
            queryset=Sector.objects.all(),
            serializer=SectorSerializer,
            serializer_fields=('url', 'code', 'name'),
            name_search_field="budgetsector__sector__name",
            renamed_name_search_field="sector_name",
        ),
        GroupBy(
            query_param="related_activity",
            fields=("activity__relatedactivity__ref_activity__id"),
            renamed_fields="related_activity",
        ),
        GroupBy(
            query_param="reporting_organisation",
            fields="activity__reporting_organisations__normalized_ref",
            renamed_fields="reporting_organisation",
            queryset=Organisation.objects.all(),
            serializer=OrganisationSerializer,
            serializer_main_field='organisation_identifier',
            name_search_field="activity__reporting_organisations__organisation__primary_name",
            renamed_name_search_field="reporting_organisation_name"
        ),
        GroupBy(
            query_param="participating_organisation",
            fields="activity__participating_organisations__primary_name",
            renamed_fields="participating_organisation",
            queryset=ActivityParticipatingOrganisation.objects.all(),
            # serializer=OrganisationSerializer,
            name_search_field="activity__participating_organisations__primary_name",
            renamed_name_search_field="participating_organisation_name"
        ),
        GroupBy(
            query_param="participating_organisation_type",
            fields="activity__participating_organisations__type",
            renamed_fields="participating_organisation_type",
            queryset=OrganisationType.objects.all(),
            serializer=CodelistSerializer,
            name_search_field="activity__participating_organisations__type__name",
            renamed_name_search_field="participating_organisations_type_name"
        ),
        GroupBy(
            query_param="document_link_category",
            fields="activity__documentlink__categories__code",
            renamed_fields="document_link_category",
            queryset=DocumentCategory.objects.all(),
            serializer=CodelistSerializer,
            name_search_field="activity__documentlink__categories__name",
            renamed_name_search_field="document_link_category_name"
        ),
        GroupBy(
            query_param="activity_status",
            fields="activity__activity_status",
            renamed_fields="activity_status",
            queryset=ActivityStatus.objects.all(),
            serializer=CodelistSerializer,
            name_search_field="activity__activity_status__name",
            renamed_name_search_field="activity_status_name"
        ),
        GroupBy(
            query_param="collaboration_type",
            fields="activity__collaboration_type",
            renamed_fields="collaboration_type",
            queryset=CollaborationType.objects.all(),
            serializer=CodelistSerializer,
            name_search_field="activity__collaboration_type__name",
            renamed_name_search_field="collaboration_type_name"
        ),
        GroupBy(
            query_param="budget_period_start_year",
            extra={
                'select': {
                    'budget_period_start_year': 'EXTRACT(YEAR FROM "period_start")::integer',
                },
                'where': [
                    'EXTRACT(YEAR FROM "period_start")::integer IS NOT NULL',
                ],
            },
            fields="budget_period_start_year",
        ),
        GroupBy(
            query_param="budget_period_end_year",
            extra={
                'select': {
                    'budget_period_end_year': 'EXTRACT(YEAR FROM "period_end")::integer',
                },
                'where': [
                    'EXTRACT(YEAR FROM "period_end")::integer IS NOT NULL',
                ],
            },
            fields="budget_period_end_year",
        ),
        GroupBy(
            query_param="budget_period_start_quarter",
            extra={
                'select': {
                    'budget_period_start_year': 'EXTRACT(YEAR FROM "period_start")::integer',
                    'budget_period_start_quarter': 'EXTRACT(QUARTER FROM "period_start")::integer',
                },
                'where': [
                    'EXTRACT(YEAR FROM "period_start")::integer IS NOT NULL',
                    'EXTRACT(QUARTER FROM "period_start")::integer IS NOT NULL',
                ],
            },
            fields=("budget_period_start_year", "budget_period_start_quarter")
        ),
        GroupBy(
            query_param="budget_period_end_quarter",
            extra={
                'select': {
                    'budget_period_end_year': 'EXTRACT(YEAR FROM "period_end")::integer',
                    'budget_period_end_quarter': 'EXTRACT(QUARTER FROM "period_end")::integer',
                },
                'where': [
                    'EXTRACT(YEAR FROM "period_end")::integer IS NOT NULL',
                    'EXTRACT(QUARTER FROM "period_end")::integer IS NOT NULL',
                ],
            },
            fields=("budget_period_end_year", "budget_period_end_quarter")
        ),
        GroupBy(
            query_param="budget_period_start_month",
            extra={
                'select': {
                    'budget_period_start_year': 'EXTRACT(YEAR FROM "period_start")::integer',
                    'budget_period_start_month': 'EXTRACT(MONTH FROM "period_start")::integer',
                },
                'where': [
                    'EXTRACT(YEAR FROM "period_start")::integer IS NOT NULL',
                    'EXTRACT(MONTH FROM "period_start")::integer IS NOT NULL',
                ],
            },
            fields=("budget_period_start_year", "budget_period_start_month")
        ),
        GroupBy(
            query_param="budget_period_end_month",
            extra={
                'select': {
                    'budget_period_end_yer': 'EXTRACT(YEAR FROM "period_end")::integer',
                    'budget_period_end_month': 'EXTRACT(MONTH FROM "period_end")::integer',
                },
                'where': [
                    'EXTRACT(YEAR FROM "period_end")::integer IS NOT NULL',
                    'EXTRACT(MONTH FROM "period_end")::integer IS NOT NULL',
                ],
            },
            fields=("budget_period_end_year", "budget_period_end_month")
        ),
    )

