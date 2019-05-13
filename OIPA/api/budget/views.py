from django.db.models import Count, F, Sum
from django_filters.rest_framework import DjangoFilterBackend

from api.budget.serializers import BudgetSerializer
from api.activity.serializers import CodelistSerializer
from api.aggregation.views import Aggregation, AggregationView, GroupBy
from api.budget import filters
from api.country.serializers import CountrySerializer
from api.generics.filters import SearchFilter
from api.generics.views import DynamicListView
from api.organisation.serializers import OrganisationSerializer
from api.region.serializers import RegionSerializer
from api.sector.serializers import SectorSerializer
from geodata.models import Country, Region
from iati.models import (
    ActivityParticipatingOrganisation, ActivityStatus, Budget,
    CollaborationType, DocumentCategory, Organisation, OrganisationType,
    Sector
)
from iati_codelists.models import BudgetType
from api.budget.filters import RelatedOrderingFilter

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
    Choose the right currency field,
    and aggregate differently based on group_by
    """
    currency = query_params.get('convert_to')

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
    Returns aggregations based on the item grouped by,
    and the selected aggregation.

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
    - `budget_type`

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
            serializer_fields=('url', 'code', 'name', 'location', 'region'),
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
            fields=(
                "activity__relatedactivity__ref_activity__iati_identifier"),
            renamed_fields="related_activity",
        ),
        GroupBy(
            query_param="reporting_organisation",
            fields="activity__reporting_organisations__organisation__id",
            renamed_fields="reporting_organisation",
            queryset=Organisation.objects.all(),
            serializer=OrganisationSerializer,
            serializer_main_field='id',
            name_search_field=  # NOQA: E251
            "activity__reporting_organisations__organisation__primary_name",
            renamed_name_search_field="reporting_organisation_name"
        ),
        GroupBy(
            query_param="participating_organisation",
            fields="activity__participating_organisations__primary_name",
            renamed_fields="participating_organisation",
            queryset=ActivityParticipatingOrganisation.objects.all(),
            name_search_field=  # NOQA: E251
            "activity__participating_organisations__primary_name",
            renamed_name_search_field="participating_organisation_name"
        ),
        GroupBy(
            query_param="participating_organisation_type",
            fields="activity__participating_organisations__type",
            renamed_fields="participating_organisation_type",
            queryset=OrganisationType.objects.all(),
            serializer=CodelistSerializer,
            name_search_field=  # NOQA: E251
            "activity__participating_organisations__type__name",
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
            query_param="budget_type",
            fields=("type"),
            queryset=BudgetType.objects.all(),
            serializer=CodelistSerializer,
        ),
        GroupBy(
            query_param="budget_period_start_year",
            extra={
                'select': {
                    'budget_period_start_year':
                        'EXTRACT(YEAR FROM "period_start")::integer',
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
                    'budget_period_end_year':
                        'EXTRACT(YEAR FROM "period_end")::integer',
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
                    'budget_period_start_year':
                        'EXTRACT(YEAR FROM "period_start")::integer',
                    'budget_period_start_quarter':
                        'EXTRACT(QUARTER FROM "period_start")::integer',
                },
                'where': [
                    'EXTRACT(YEAR FROM "period_start")::integer IS NOT NULL',
                    'EXTRACT(QUARTER FROM "period_start")::integer IS NOT NULL'
                ],
            },
            fields=("budget_period_start_year", "budget_period_start_quarter")
        ),
        GroupBy(
            query_param="budget_period_end_quarter",
            extra={
                'select': {
                    'budget_period_end_year':
                        'EXTRACT(YEAR FROM "period_end")::integer',
                    'budget_period_end_quarter':
                        'EXTRACT(QUARTER FROM "period_end")::integer',
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
                    'budget_period_start_year':
                        'EXTRACT(YEAR FROM "period_start")::integer',
                    'budget_period_start_month':
                        'EXTRACT(MONTH FROM "period_start")::integer',
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
                    'budget_period_end_yer':
                        'EXTRACT(YEAR FROM "period_end")::integer',
                    'budget_period_end_month':
                        'EXTRACT(MONTH FROM "period_end")::integer',
                },
                'where': [
                    'EXTRACT(YEAR FROM "period_end")::integer IS NOT NULL',
                    'EXTRACT(MONTH FROM "period_end")::integer IS NOT NULL',
                ],
            },
            fields=("budget_period_end_year", "budget_period_end_month")
        ),
    )


class BudgetList(DynamicListView):
    """
    Returns a list of IATI Budget stored in OIPA.

    ## Filter parameters
    - `activity_id` (*optional*): Comma separated list of activity id's.
    - `type` (*optional*): Comma separated list of activity id's.
    """

    queryset = Budget.objects.all()
    filter_backends = (
        SearchFilter,
        DjangoFilterBackend,
        RelatedOrderingFilter,
    )
    filter_class = filters.BudgetFilter
    serializer_class = BudgetSerializer

    # make sure we can always have info about selectable fields,
    # stored into dict. This dict is populated in the DynamicView class using
    # _get_query_fields methods.
    selectable_fields = ()
    break_down_by = 'sectors'

    # Required fields for the serialisation defined by the
    # specification document
    fields = (
        'iati_identifier',
        'sectors',
        'recipient_regions',
        'recipient_countries',
        'budgets'

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
    exceptional_fields = [{'budgets': []}]  # NOQA: E501

    '''
    # Required fields for the serialisation defined by the
    # specification document
    fields = (
        'activity_id',
        'type',
        'status',
        'period_start',
        'period_end',
        'value',
        'iati_identifier',
        'sectors',
        'recipient_countries',
        'recipient_regions'
    )
    '''
