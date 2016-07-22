from api.transaction.serializers import TransactionSerializer
from api.transaction.filters import TransactionFilter, TransactionAggregationFilter
from iati.transaction.models import Transaction
from api.generics.views import DynamicListView, DynamicDetailView

from rest_framework.filters import DjangoFilterBackend
from rest_framework.generics import GenericAPIView
from api.activity.serializers import ActivitySerializer

from geodata.models import Country
from geodata.models import Region
from iati.models import Sector
from iati.models import ActivityStatus
from iati.models import PolicyMarker
from iati.models import TransactionType
from iati.models import CollaborationType
from iati.models import DocumentCategory
from iati.models import FlowType
from iati.models import AidType
from iati.models import FinanceType
from iati.models import TiedStatus
from iati.models import ActivityParticipatingOrganisation
from iati.models import OrganisationType
from iati.models import Organisation
from iati.models import ActivityReportingOrganisation

from api.activity.serializers import CodelistSerializer
from api.country.serializers import CountrySerializer
from api.region.serializers import RegionSerializer
from api.sector.serializers import SectorSerializer
from api.organisation.serializers import OrganisationSerializer

from api.pagination import CustomTransactionPagination


class TransactionList(DynamicListView):
    """
    Returns a list of IATI Transactions stored in OIPA.

    ## Request parameters

    - `id` (*optional*): Transaction identifier.
    - `aid_type` (*optional*): Aid type identifier.
    - `activity` (*optional*): Comma separated list of activity id's.
    - `transaction_type` (*optional*): Transaction type identifier.
    - `value` (*optional*): Transaction value.
    - `min_value` (*optional*): Minimal transaction value.
    - `max_value` (*optional*): Maximal transaction value.
    - `q` (*optional*): Search specific value in activities list.
        See [Searching]() section for details.
    - `fields` (*optional*): List of fields to display.

    ## Searching

    - `description`
    - `provider_organisation_name`
    - `receiver_organisation_name`

    ## Result details

    Each result item contains short information about transaction including URI to transaction details.

    URI is constructed as follows: `/api/transactions/{transaction_id}`

    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filter_class = TransactionFilter
    pagination_class = CustomTransactionPagination

    fields = (
        'url',
        'activity',
        'provider_organisation',
        'receiver_organisation',
        'currency',
        'transaction_type',
        'value_date',
        'value',
    )

    search_fields = (
        'description',
        'provider_organisation',
        'receiver_organisation',
    )

class TransactionDetail(DynamicDetailView):
    """
    Returns detailed information about Transaction.

    ## URI Format

    ```
    /api/transactions/{transaction_id}
    ```

    ### URI Parameters

    - `transaction_id`: Numerical ID of desired Transaction

    ## Request parameters

    - `fields` (*optional*): List of fields to display

    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


from django.db.models import Count, Sum, Q, F

from api.generics.filters import SearchFilter
from api.aggregation.views import AggregationView, Aggregation, GroupBy

from geodata.models import Country, Region
from api.country.serializers import CountrySerializer
from api.region.serializers import RegionSerializer
from api.activity.serializers import RelatedActivitySerializer, SectorSerializer

from iati.models import Activity, RelatedActivity, Sector
from iati.models import ActivityParticipatingOrganisation
from iati.models import ActivityReportingOrganisation

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
    
    if currency: currency = currency.lower()

    if currency is None or currency not in currencies:
        currency_field = 'value'
    else:
        currency_field = currency + '_value'

    annotation_components = F(currency_field)

    param_additions = []

    for param in query_params:
        if param == 'recipient_country':
            param_additions.append('transactionrecipientcountry__percentage')
        elif param == 'recipient_region':
            param_additions.append('transactionrecipientregion__percentage')
        elif param == 'sector':
            param_additions.append('transactionsector__percentage')

    grouping_additions = []

    for grouping in groupings:
        if grouping.query_param == 'recipient_country':
            grouping_additions.append('transactionrecipientcountry__percentage')
        elif grouping.query_param == 'recipient_region':
            grouping_additions.append('transactionrecipientregion__percentage')
        elif grouping.query_param == 'sector':
            grouping_additions.append('transactionsector__percentage')

    additions = list(set(param_additions).union(grouping_additions))

    for percentage_field in additions:
        percentage_expression = F(percentage_field) / 100.0
        annotation_components = annotation_components * percentage_expression

    return Sum(annotation_components)


class TransactionAggregation(AggregationView):
    """
    Returns aggregations based on the item grouped by, and the selected aggregation.

    ## Group by options

    API request has to include `group_by` parameter.
    
    This parameter controls result aggregations and
    can be one or more (comma separated values) of:

    - `recipient_country`
    - `recipient_region`
    - `sector`
    - `related_activity`
    - `transaction_type`
    - `reporting_organisation`
    - `participating_organisation`
    - `receiver_org`
    - `provider_org`
    - `document_link_category`
    - `activity_status`
    - `participating_organisation_type`
    - `collaboration_type`
    - `default_flow_type`
    - `default_finance_type`
    - `default_aid_type`
    - `default_tied_status`
    - `transactions_per_quarter`
    - `transaction_date_year`

    ## Aggregation options

    API request has to include `aggregations` parameter.
    
    This parameter controls result aggregations and
    can be one or more (comma separated values) of:

    - `count`
    - `activity_count`
    - `value`
    - `disbursement`
    - `expenditure`
    - `commitment`
    - `incoming_fund`

    ## Currency options

    By default the values returned by the aggregations are in the reported currency. This only renders meaningful results when all values were in the same currency. Which is only the case when you filter your results down.

    The aggregation endpoints have the ability to return values in a currency. Options for this `convert_to` parameter are:

    - `xdr`
    - `usd`
    - `eur`
    - `gbp`
    - `jpy`
    - `cad`

    This results in converted values when the original value was in another currency. 

    Information on used exchange rates can be found <a href='https://docs.oipa.nl/'>in the docs</a>.


    ## Request parameters

    All filters available on the Transaction List, can be used on aggregations.

    """

    queryset = Transaction.objects.all()

    filter_backends = (SearchFilter, DjangoFilterBackend,)
    filter_class = TransactionAggregationFilter

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
        Aggregation(
            query_param='incoming_fund',
            field='incoming_fund',
            annotate=annotate_currency,
            extra_filter=Q(transaction_type=1),
        ),
        Aggregation(
            query_param='commitment',
            field='commitment',
            annotate=annotate_currency,
            extra_filter=Q(transaction_type=2),
        ),
        Aggregation(
            query_param='disbursement',
            field='disbursement',
            annotate=annotate_currency,
            extra_filter=Q(transaction_type=3),
        ),
        Aggregation(
            query_param='expenditure',
            field='expenditure',
            annotate=annotate_currency,
            extra_filter=Q(transaction_type=4),
        ),
    )

    allowed_groupings = (
        GroupBy(
            query_param="recipient_country",
            fields="transactionrecipientcountry__country",
            renamed_fields="recipient_country",
            queryset=Country.objects.all(),
            serializer=CountrySerializer,
            serializer_fields=('url', 'code', 'name', 'location'),
            name_search_field='transactionrecipientcountry__country__name',
            renamed_name_search_field='recipient_country_name',
        ),
        GroupBy(
            query_param="recipient_region",
            fields="transactionrecipientregion__region",
            renamed_fields="recipient_region",
            queryset=Region.objects.all(),
            serializer=RegionSerializer,
            serializer_fields=('url', 'code', 'name', 'location'),
            name_search_field="transactionrecipientregion__region__name",
            renamed_name_search_field="recipient_region_name",
        ),
        GroupBy(
            query_param="sector",
            fields="transactionsector__sector",
            renamed_fields="sector",
            queryset=Sector.objects.all(),
            serializer=SectorSerializer,
            serializer_fields=('url', 'code', 'name', 'location'),
            name_search_field="sector__name",
            renamed_name_search_field="sector_name",
        ),
        GroupBy(
            query_param="related_activity",
            fields=("activity__relatedactivity__ref_activity__id"),
            renamed_fields="related_activity",
        ),
        GroupBy(
            query_param="transaction_type",
            fields=("transaction_type"),
            queryset=TransactionType.objects.all(),
            serializer=CodelistSerializer,
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
            fields=("activity__participating_organisations__primary_name", "activity__participating_organisations__normalized_ref"),
            renamed_fields=("participating_organisation", "participating_organisation_ref"),
            queryset=ActivityParticipatingOrganisation.objects.all(),
            name_search_field="activity__participating_organisations__primary_name",
            renamed_name_search_field="participating_organisation_name"
        ),
        GroupBy(
            query_param="provider_org",
            fields=("provider_organisation__primary_name"),
            renamed_fields="provider_org",
            name_search_field="provider_organisation__primary_name",
            renamed_name_search_field="provider_org_name"
        ),
        GroupBy(
            query_param="receiver_org",
            fields=("receiver_organisation__primary_name"),
            renamed_fields="receiver_org",
            name_search_field="receiver_organisation__primary_name",
            renamed_name_search_field="receiver_org_name"
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
            query_param="participating_organisation_type",
            fields="activity__participating_organisations__type",
            renamed_fields="participating_organisation_type",
            queryset=OrganisationType.objects.all(),
            serializer=CodelistSerializer,
            name_search_field="activity__participating_organisations__type__name",
            renamed_name_search_field="participating_organisations_type_name"
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
            query_param="default_flow_type",
            fields="activity__default_flow_type",
            renamed_fields="default_flow_type",
            queryset=FlowType.objects.all(),
            serializer=CodelistSerializer,
        ),
        GroupBy(
            query_param="default_finance_type",
            fields="activity__default_finance_type",
            renamed_fields="default_finance_type",
            queryset=FinanceType.objects.all(),
            serializer=CodelistSerializer,
        ),
        GroupBy(
            query_param="default_aid_type",
            fields="activity__default_aid_type",
            renamed_fields="default_aid_type",
            queryset=AidType.objects.all(),
            serializer=CodelistSerializer,
        ),
        GroupBy(
            query_param="default_tied_status",
            fields="activity__default_tied_status",
            renamed_fields="default_tied_status",
            queryset=TiedStatus.objects.all(),
            serializer=CodelistSerializer,
        ),
        GroupBy(
            query_param="transaction_date_year",
            extra={
                'select': {
                    'transaction_date_year': 'EXTRACT(YEAR FROM "transaction_date")::integer',
                },
                'where': [
                    'EXTRACT(YEAR FROM "transaction_date")::integer IS NOT NULL',
                ],
            },
            fields="transaction_date_year",
        ),
        GroupBy(
            query_param="transaction_date_month",
            extra={
                'select': {
                    'transaction_date_year': 'EXTRACT(YEAR FROM "transaction_date")::integer',
                    'transaction_date_month': 'EXTRACT(MONTH FROM "transaction_date")::integer',
                },
                'where': [
                    'EXTRACT(YEAR FROM "transaction_date")::integer IS NOT NULL',
                    'EXTRACT(MONTH FROM "transaction_date")::integer IS NOT NULL',
                ],
            },
            fields=("transaction_date_year", "transaction_date_month")
        ),
    )

