import uuid
import gc

from rest_framework import filters
from haystack.query import SearchQuerySet
from haystack.inputs import Exact

from django.db.models.sql.constants import QUERY_TERMS
from django.db.models import Q
from django_filters import CharFilter
from django_filters import Filter, FilterSet, NumberFilter, DateFilter, BooleanFilter

VALID_LOOKUP_TYPES = sorted(QUERY_TERMS)


class SearchFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):

        query = request.query_params.get('q', None)
        exact = request.query_params.get('exact', None)

        if query:
            # always match text exactly
            if exact: query = Exact(query)

            search_queryset = SearchQuerySet()
            query_fields = request.query_params.get('q_fields')
            if query_fields:
                query_fields = query_fields.split(',')
                for query_field in query_fields:
                    filter_dict = {query_field:query}
                    search_queryset = search_queryset.filter_or(**filter_dict)
            else:
                search_queryset = search_queryset.filter_or(text=query)

            activity_ids = search_queryset.values_list('pk',flat=True)[0:100000]

            return queryset.filter(pk__in=activity_ids).filter(is_searchable=True)

        return queryset

class CommaSeparatedCharFilter(CharFilter):

    def filter(self, qs, value):

        if value:
            value = value.split(',')

        self.lookup_type = 'in'

        return super(CommaSeparatedCharFilter, self).filter(qs, value)

class CommaSeparatedCharMultipleFilter(CharFilter):
    """
    Comma separated filter for lookups like 'exact', 'iexact', etc..
    """
    def filter(self, qs, value):
        if not value: return qs

        values = value.split(',')

        lookup_type = self.lookup_type

        filters = [Q(**{"{}__{}".format(self.name, lookup_type): value}) for value in values]
        final_filters = reduce(lambda a, b: a | b, filters)

        return qs.filter(final_filters)

class CommaSeparatedDateRangeFilter(Filter):

    def filter(self, qs, value):

        if value in ([], (), {}, None, ''):
            return qs

        values = value.split(',')

        return super(CommaSeparatedDateRangeFilter, self).filter(qs, values)

class TogetherFilter(Filter):
    """
    Used with TogetherFilterSet, always gets called regardless of GET args
    """
    
    def __init__(self, filters=None, values=None, **kwargs):
        self.filter_classes = filters
        self.values = values

        super(TogetherFilter, self).__init__(**kwargs)

    def filter(self, qs, values):
        if self.filter_classes:
            filters = { "%s__%s" % (c[0].name, c[0].lookup_type) : c[1] for c in zip(self.filter_classes, values)}
            qs = qs.filter(**filters).distinct()

            return qs

class TogetherFilterSet(FilterSet):
    def __init__(self, data=None, queryset=None, prefix=None, strict=None):
        """
        Adds a together_exclusive meta option that selects fields that have to 
        be called in the same django filter() call when both present
        """

        meta = getattr(self, 'Meta', None)

        # fields that must be filtered in the same filter call
        self.together_exclusive = getattr(meta, 'together_exclusive', None)

        data = data.copy()

        for filterlist in self.together_exclusive:
            if set(filterlist).issubset(data.keys()):

                filter_values = [data.pop(filteritem)[0] for filteritem in filterlist]
                filter_classes = [self.declared_filters.get(filteritem, None) for filteritem in filterlist]

                uid = uuid.uuid4()

                self.base_filters[uid] = TogetherFilter(filters=filter_classes)
                data.appendlist(uid, filter_values)

        super(FilterSet, self).__init__(data, queryset, prefix, strict)

