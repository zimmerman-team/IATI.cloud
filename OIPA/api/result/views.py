from django.db.models import Count, F, Func, Sum
from django_filters.rest_framework import DjangoFilterBackend

from api.activity.serializers import ResultSerializer
from api.aggregation.views import Aggregation, AggregationView, GroupBy
from api.generics.filters import SearchFilter
from api.generics.views import DynamicListView
from api.result.filters import RelatedOrderingFilter, ResultFilter
from iati.models import Result


class ResultAggregations(AggregationView):
    """
    Returns aggregations based on the item grouped by,
    and the selected aggregation.

    ## Group by options

    API request has to include `group_by` parameter.

    This parameter controls result aggregations and
    can be one or more (comma separated values) of:

    - `result_indicator_title`
    - `result_title`


    ## Aggregation options

    API request has to include `aggregations` parameter.

    This parameter controls result aggregations and
    can be one or more (comma separated values) of:

    - `target` Indicator period target. Currently breaks on non number results.
    - `actual` Indicator period actual. Currently breaks on non number results.

    ## Request parameters

    All filters available on the Activity List, can be used on aggregations.

    """

    queryset = Result.objects.all()
    filter_backends = (SearchFilter, DjangoFilterBackend,)
    filter_class = ResultFilter

    allowed_aggregations = (
        Aggregation(
            query_param='targets',
            field='targets',
            annotate=Sum(Func(
                F('resultindicator__resultindicatorperiod__targets__value'),
                function='CAST',
                template='%(function)s(%(expressions)s as double precision)')),
        ),
        Aggregation(
            query_param='actuals',
            field='actuals',
            annotate=Sum(Func(
                F('resultindicator__resultindicatorperiod__actuals__value'),
                function='CAST',
                template='%(function)s(%(expressions)s as double precision)')),
        ),
        Aggregation(
            query_param='activity_count',
            field='activity_count',
            annotate=Count('activity', distinct=True),
        ),
    )

    allowed_groupings = (
        GroupBy(
            query_param="result_indicator_title",
            fields=("resultindicator__resultindicatortitle__primary_name"),
            renamed_fields="result_indicator_title"
        ),
        GroupBy(
            query_param="result_title",
            fields=("resulttitle__narratives__content"),
            renamed_fields="result_title"
        ),
    )


class ResultList(DynamicListView):
    queryset = Result.objects.all()
    filter_backends = (
        SearchFilter,
        DjangoFilterBackend,
        RelatedOrderingFilter,
    )
    filter_class = ResultFilter
    serializer_class = ResultSerializer

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
        'results'

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
    exceptional_fields = [{'results': []}]
