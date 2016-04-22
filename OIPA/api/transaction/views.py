from api.transaction.serializers import TransactionSerializer
from api.transaction.filters import TransactionFilter
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
from iati.models import CollaborationType
from iati.models import DocumentCategory
from iati.models import FlowType
from iati.models import AidType
from iati.models import FinanceType
from iati.models import TiedStatus
from iati.models import ActivityParticipatingOrganisation
from iati.models import OrganisationType
from iati.models import ActivityReportingOrganisation

from api.activity.serializers import CodelistSerializer
from api.country.serializers import CountrySerializer
from api.region.serializers import RegionSerializer
from api.sector.serializers import SectorSerializer

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

from api.activity.filters import SearchFilter
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

    if currency is None or currency not in currencies:
        currency_field = 'value'
    else:
        currency_field = currency + '_value'

    for grouping in groupings:
        if grouping.query_param == "recipient_country":
            return Sum(F(currency_field) * (F('transactionrecipientcountry__percentage') / 100.0))
        elif grouping.query_param == "recipient_region":
            return Sum(F(currency_field) * (F('transactionrecipientregion__percentage') / 100.0))
        elif grouping.query_param == "sector":
            return Sum(F(currency_field) * (F('transactionsector__percentage') / 100.0))
        else:
            return Sum('value')

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
    - `reporting_organisation`
    - `participating_organisation`
    - `document_link_category`
    - `activity_status`
    - `participating_organisation_type`
    - `policy_marker`
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
    filter_class = TransactionFilter

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
        ),
        GroupBy(
            query_param="recipient_region",
            fields="transactionrecipientregion__region",
            renamed_fields="recipient_region",
            queryset=Region.objects.all(),
            serializer=RegionSerializer,
            serializer_fields=('url', 'code', 'name', 'location'),
        ),
        GroupBy(
            query_param="sector",
            fields="transactionsector__sector",
            renamed_fields="sector",
            queryset=Sector.objects.all(),
            serializer=SectorSerializer,
            serializer_fields=('url', 'code', 'name', 'location'),
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
            queryset=ActivityReportingOrganisation.objects.all(),
            # serializer=OrganisationSerializer,
        ),
        GroupBy(
            query_param="participating_organisation",
            fields="activity__participating_organisations__normalized_ref",
            renamed_fields="participating_organisation",
            queryset=ActivityParticipatingOrganisation.objects.all(),
            # serializer=OrganisationSerializer,
        ),
        GroupBy(
            query_param="document_link_category",
            fields="activity__documentlink__categories__code",
            renamed_fields="document_link_category",
            queryset=DocumentCategory.objects.all(),
            serializer=CodelistSerializer,
        ),
        GroupBy(
            query_param="activity_status",
            fields="activity__activity_status",
            renamed_fields="activity_status",
            queryset=ActivityStatus.objects.all(),
            serializer=CodelistSerializer,
        ),
        GroupBy(
            query_param="participating_organisation_type",
            fields="activity__participating_organisations__type",
            renamed_fields="participating_organisation_type",
            queryset=OrganisationType.objects.all(),
            serializer=CodelistSerializer,
        ),
        GroupBy(
            query_param="policy_marker",
            fields="activity__policy_marker",
            renamed_fields="policy_marker",
            queryset=PolicyMarker.objects.all(),
            serializer=CodelistSerializer,
        ),
        GroupBy(
            query_param="collaboration_type",
            fields="activity__collaboration_type",
            renamed_fields="collaboration_type",
            queryset=CollaborationType.objects.all(),
            serializer=CodelistSerializer,
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
        # TODO: Make these a full date object instead - 2016-04-12
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

