from api.result.filters import ResultFilter
from api.aggregation.views import AggregationView, Aggregation, GroupBy
from django.db.models import Sum, Func, F, Count
from iati.models import Result
from rest_framework.filters import DjangoFilterBackend
from api.generics.filters import SearchFilter


class ResultAggregations(AggregationView):
    """
    Returns aggregations based on the item grouped by, and the selected aggregation.

    ## Group by options

    API request has to include `group_by` parameter.
    
    This parameter controls result aggregations and
    can be one or more (comma separated values) of:

    - `result_indicator_title`


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
            query_param='target',
            field='target',
            annotate=Sum(Func(
                F('resultindicator__resultindicatorperiod__target'), 
                function='CAST', 
                template='%(function)s(%(expressions)s as double precision)')),
        ),
        Aggregation(
            query_param='actual',
            field='actual',
            annotate=Sum(Func(
                F('resultindicator__resultindicatorperiod__actual'), 
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

