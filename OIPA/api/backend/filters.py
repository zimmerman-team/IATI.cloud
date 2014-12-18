from rest_framework import filters


class SearchFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        query = request.QUERY_PARAMS.get('q', None)
        if query:
            query_fields = request.QUERY_PARAMS.get('q_fields')
            if query_fields:
                query_fields = query_fields.split(',')
            return queryset.search(query, query_fields)
        return queryset.all()
