import uuid
import operator
from django.conf import settings
from django.db.models.sql.constants import QUERY_TERMS
from django.db.models import Q
from django_filters import CharFilter
from django_filters import Filter, FilterSet, BooleanFilter
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from rest_framework import filters
from iati.djorm_pgfulltext.fields import TSConfig
from iati.models import Activity, Document
from iati.models import Location
from common.util import combine_filters
from functools import reduce

VALID_LOOKUP_TYPES = sorted(QUERY_TERMS)


def reduce_comma(arr, value):
    """
    urls are already unescaped when arriving in filters.

    In case the filter is on a name that contains a comma,
    this should be treated as 1 filter instead of 2:

    Example: "Wageningen, University of"

    before: ["Wageningen", " University of"]
    after: ["Wageningen, University of"]

    This only works when there's a space behind the comma.
    """
    if value[:1] == ' ' and len(arr):
        arr[len(arr) - 1] = arr[len(arr) - 1] + "," + value
    else:
        arr.append(value)
    return arr


class DistanceFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):

        location_longitude = request.query_params.get('location_longitude', None)
        location_latitude = request.query_params.get('location_latitude', None)
        distance_km = request.query_params.get('location_distance_km', None)

        if location_longitude and location_latitude and distance_km:
            pnt = GEOSGeometry(
                'POINT({0} {1})'.format(
                    location_longitude,
                    location_latitude),
                srid=4326)

            if Location is not queryset.model:
                model_prefix = 'location__'
            else:
                model_prefix = ''

            loc_ids = Location.objects.filter(
                **{'point_pos__distance_lte': (pnt, D(km=distance_km))}).values('id')

            return queryset.filter(**{"{}id__in".format(model_prefix): loc_ids})

        return queryset


class SearchFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):

        query = request.query_params.get('q', None)
        query_lookup = request.query_params.get('q_lookup', None)
        lookup_expr = 'exact'  # 'ft'
        if query_lookup:
            lookup_expr = query_lookup

        if query:

            query_fields = request.query_params.get('q_fields')
            #dict_query_list = [TSConfig('simple'), query]
            #print(dict_query_list)
            model_prefix = ''

            # when SearchFilter is used on other endpoints than activities,
            # add activity__ to the filter name
            if Activity is not queryset.model:
                model_prefix = 'activity__'

            # if root organisations set, only query searchable activities
            if settings.ROOT_ORGANISATIONS:
                queryset = queryset.filter(**{'{0}is_searchable'.format(model_prefix): True})

            if query_fields:
                query_fields = query_fields.split(',')

                if isinstance(query_fields, list):
                    filters = ([{'{0}activitysearch__{1}__{2}'.format(model_prefix, field, lookup_expr) : query}for field in query_fields])
                    temp = Q(**filters.pop())
                    
                    for f in filters:
                        temp |= Q(**f)                    
                    return queryset.filter(temp)
            else:
                return queryset.filter(
                    **{'{0}activitysearch__search_vector_text__{1}'.format(model_prefix, lookup_expr): query})

        return queryset


class DocumentSearchFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):

        query = request.query_params.get('document_q', None)
        query_lookup = request.query_params.get('q_lookup', None)
        lookup_expr = 'ft'
        if query_lookup:
            if query_lookup == 'exact':
                lookup_expr = 'ft'
            if query_lookup == 'startswith':
                lookup_expr = 'ft_startswith'

        if query:

            query_fields = request.query_params.get('q_fields')
            dict_query_list = [TSConfig('simple'), query]

            model_prefix = ''

            # when SearchFilter is used on other endpoints than activities,
            # add activity__ to the filter name
            if Document is not queryset.model:
                model_prefix = 'document__'

            # if root organisations set, only query searchable activities
            # if settings.ROOT_ORGANISATIONS:
            #     queryset = queryset.filter(**{'{0}is_searchable'.format(model_prefix): True})

            return queryset.filter(
                **{'{0}documentsearch__text__{1}'.format(model_prefix, lookup_expr): dict_query_list})

        return queryset


class CommaSeparatedCharFilter(CharFilter):

    def filter(self, qs, value):

        if value:
            value = value.split(',')
            value = reduce(reduce_comma, value, [])

        self.lookup_expr = 'in'

        return super(CommaSeparatedCharFilter, self).filter(qs, value)


class StickyCharFilter(CharFilter):

    def filter(self, qs, value):
        qs._next_is_sticky()
        return super(StickyCharFilter, self).filter(qs, value)


class CommaSeparatedStickyCharFilter(CharFilter):

    def filter(self, qs, value):

        if value:
            value = value.split(',')
            value = reduce(reduce_comma, value, [])

        self.lookup_expr = 'in'
        qs._next_is_sticky()

        return super(CommaSeparatedStickyCharFilter, self).filter(qs, value)


class StickyBooleanFilter(BooleanFilter):
    """
    Comma separated filter for lookups like 'exact', 'iexact', etc..
    """

    def filter(self, qs, value):
        qs._next_is_sticky()

        return super(StickyBooleanFilter, self).filter(qs, value)


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

    def __init__(self, filters=None, values=None, *args, **kwargs):
        self.filter_classes = filters
        self.values = values

        super(TogetherFilter, self).__init__(*args, **kwargs)

    def filter(self, qs, values):
        if self.filter_classes:
            filters = {"%s__%s" % (c[0].name, c[0].lookup_expr): c[1]
                       for c in zip(self.filter_classes, values)}
            qs = qs.filter(**filters)

            return qs


class TogetherFilterSet(FilterSet):

    def __init__(self, data=None, queryset=None, prefix=None, strict=None, *args, **kwargs):
        """
        Adds a together_exclusive meta option that selects fields that have to
        be called in the same django filter() call when both present
        """

        meta = getattr(self, 'Meta', None)

        # fields that must be filtered in the same filter call
        together_exclusive = getattr(meta, 'together_exclusive', [])

        if data:
            data = data.copy()
        else:
            data = {}

        for filterlist in together_exclusive:
            if set(filterlist).issubset(data.keys()):

                filter_values = [data.pop(filteritem)[0] for filteritem in filterlist]
                filter_classes = [
                    self.declared_filters.get(
                        filteritem,
                        None) for filteritem in filterlist]

                uid = unicode(uuid.uuid4())

                self.base_filters[uid] = TogetherFilter(filters=filter_classes)
                data.appendlist(uid, filter_values)

        super(FilterSet, self).__init__(data, queryset, prefix, strict, *args, **kwargs)


# class SubFilterSet(FilterSet):
#     """
#     Use a FilterSet as a sub filterset for another filterset
#     """

#     __metaclass__ = SubFilterSetMetaClass

#     def __init__(self, data=None, queryset=None, prefix=None, strict=None):

#         meta = getattr(self, 'Meta', None)

#         sub_filtersets = getattr(meta, 'sub_filtersets', [])

#         data = data.copy()

#         for filterset in sub_filtersets:


class CommaSeparatedCharMultipleFilter(CharFilter):
    """
    Comma separated filter for lookups like 'exact', 'iexact', etc..
    """

    def filter(self, qs, value):
        if not value:
            return qs

        values = value.split(',')
        values = reduce(reduce_comma, values, [])

        lookup_expr = self.lookup_expr

        if lookup_expr is 'in':
            final_filters = Q(**{"{}__{}".format(self.name, lookup_expr): values})
        else:
            filters = [Q(**{"{}__{}".format(self.name, lookup_expr): value}) for value in values]
            final_filters = reduce(lambda a, b: a | b, filters)

        return qs.filter(final_filters)


class ToManyFilter(CommaSeparatedCharMultipleFilter):
    """
    An in filter for a to-many field, where the IN is executed as a subfilter
    e.g. instead of
    SELECT "iati_activity"."id" FROM "iati_activity" LEFT OUTER JOIN "iati_activityreportingorganisation" as r ON r.activity_id = iati_activity.id  WHERE "r"."ref" IN ('US-USAGOV');

    we do:

    SELECT "iati_activity"."id" FROM "iati_activity" WHERE "iati_activity"."id" IN (SELECT U0."activity_id" FROM "iati_activityreportingorganisation" U0 WHERE U0."ref" = 'US-USAGOV');

    qs: The queryset which will be queried
    fk: The foreign key that relates back to the main_fk
    main_fk: The key being filtered on
    """

    def __init__(self, qs=None, fk=None, main_fk="id", **kwargs):
        if not qs:
            raise ValueError("qs must be specified")
        if not fk:
            raise ValueError("fk must be specified, that relates back to the main model")

        self.nested_qs = qs
        self.fk = fk
        self.main_fk = main_fk

        super(ToManyFilter, self).__init__(**kwargs)

    def filter(self, qs, value):
        if not value:
            return qs

        nested_qs = self.nested_qs.objects.all()
        nested_qs = super(ToManyFilter, self).filter(nested_qs, value)

        # nested_qs = self.nested_qs.objects.all().filter(in_filter).values(self.fk)
        in_filter = {
            "{}__in".format(self.main_fk): nested_qs.values(self.fk)
        }

        return qs.filter(**in_filter)

        # return qs.filter(id__in=nested_qs.values(self.fk))


class ToManyNotInFilter(CommaSeparatedCharMultipleFilter):
    """
    Same as ToManyFilter, but as a not in filter.
    """

    def __init__(self, qs=None, fk=None, main_fk="id", **kwargs):
        if not qs:
            raise ValueError("qs must be specified")
        if not fk:
            raise ValueError("fk must be specified, that relates back to the main model")

        self.nested_qs = qs
        self.fk = fk
        self.main_fk = main_fk

        super(ToManyNotInFilter, self).__init__(**kwargs)

    def filter(self, qs, value):
        if not value:
            return qs

        nested_qs = self.nested_qs.objects.all()
        nested_qs = super(ToManyNotInFilter, self).filter(nested_qs, value)

        in_filter = {
            "{}__in".format(self.main_fk): nested_qs.values(self.fk)
        }

        return qs.exclude(**in_filter)


class NestedFilter(CommaSeparatedCharMultipleFilter):
    """
    An in filter for a to-many field, where the IN is executed as a subfilter
    e.g. instead of
    SELECT "iati_activity"."id" FROM "iati_activity" LEFT OUTER JOIN "iati_activityreportingorganisation" as r ON r.activity_id = iati_activity.id  WHERE "r"."ref" IN ('US-USAGOV');

    we do:

    SELECT "iati_activity"."id" FROM "iati_activity" WHERE "iati_activity"."id" IN (SELECT U0."activity_id" FROM "iati_activityreportingorganisation" U0 WHERE U0."ref" = 'US-USAGOV');
    """

    def __init__(self, nested_filter=None, fk=None, **kwargs):
        if not nested_filter:
            raise ValueError("qs must be specified")
        if not fk:
            raise ValueError("fk must be specified, that relates back to the main model")

        self.nested_filter = nested_filter
        self.fk = fk

        super(NestedFilter, self).__init__(**kwargs)

    def filter(self, qs, value):
        if not value:
            return qs

        return qs.filter(id__in=self.nested_filter.filter(qs, value))
