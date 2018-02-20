from iati_synchroniser.models import Publisher
from django.db.models import Q
from django_filters import Filter
from django_filters import FilterSet
from django_filters import BooleanFilter


class SearchQueryFilter(Filter):

    def filter(self, qs, value):
        if value:
            return qs.filter(Q(publisher_iati_id__icontains=value)
                             | Q(display_name__icontains=value))
        return qs


class PublisherFilter(FilterSet):
    """
    Filter publisher list
    """

    q = SearchQueryFilter()
    no_datasets = BooleanFilter(lookup_expr='isnull', name='dataset', distinct=True)

    class Meta:
        model = Publisher
        fields = [
            'id',
            'iati_id',
            'publisher_iati_id',
            'display_name',
            'name',
            'q',
            'no_datasets']
