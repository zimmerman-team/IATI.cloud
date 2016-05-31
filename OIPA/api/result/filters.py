from api.generics.filters import TogetherFilterSet
from api.generics.filters import ToManyFilter
from api.generics.filters import CommaSeparatedCharFilter

from iati.models import Result
from iati.models import ResultTitle
from iati.models import ResultIndicatorTitle


class ResultFilter(TogetherFilterSet):

    activity_id = CommaSeparatedCharFilter(
        name='activity__id',
        lookup_type='in')

    result_title = ToManyFilter(
        qs=ResultTitle,
        lookup_type='in',
        name='primary_name',
        fk='result',
    )

    indicator_title = ToManyFilter(
        qs=ResultIndicatorTitle,
        lookup_type='in',
        name='primary_name',
        fk='result__indicator',
    )

    class Meta:
        model = Result