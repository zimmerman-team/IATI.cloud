from iati_synchroniser.models import Publisher
from django.db.models import Q
from django_filters import Filter, FilterSet


class SearchQueryFilter(Filter):

    def filter(self, qs, value):
        if value:
            return qs.filter(Q(publisher_iati_id__icontains=value) | Q(display_name__icontains=value))
        return qs


class PublisherFilter(FilterSet):
    """
    Filter publisher list
    """

    q = SearchQueryFilter()

    class Meta:
        model = Publisher
        fields = [
            'id',
            'iati_id',
            'publisher_iati_id',
            'display_name',
            'name',
            'q']

