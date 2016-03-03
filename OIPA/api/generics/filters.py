import uuid
import gc

from django.db.models.sql.constants import QUERY_TERMS
from django.db.models import Q
from django_filters import CharFilter
from django_filters import Filter, FilterSet, NumberFilter, DateFilter, BooleanFilter

VALID_LOOKUP_TYPES = sorted(QUERY_TERMS)

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
            qs = qs.filter(**filters)

            return qs

class TogetherFilterSet(FilterSet):
    def __init__(self, data=None, queryset=None, prefix=None, strict=None):
        """
        Adds a together_exclusive meta option that selects fields that have to 
        be called in the same django filter() call when both present
        """

        meta = getattr(self, 'Meta', None)

        # fields that must be filtered in the same filter call
        together_exclusive = getattr(meta, 'together_exclusive', [])

        data = data.copy()

        for filterlist in together_exclusive:
            if set(filterlist).issubset(data.keys()):

                filter_values = [data.pop(filteritem)[0] for filteritem in filterlist]
                filter_classes = [self.declared_filters.get(filteritem, None) for filteritem in filterlist]

                uid = unicode(uuid.uuid4())

                self.base_filters[uid] = TogetherFilter(filters=filter_classes)
                data.appendlist(uid, filter_values)

        super(FilterSet, self).__init__(data, queryset, prefix, strict)


class CommaSeparatedCharMultipleFilter(CharFilter):
    """
    Comma separated filter for lookups like 'exact', 'iexact', etc..
    """
    def filter(self, qs, value):
        if not value: return qs

        values = value.split(',')

        lookup_type = self.lookup_type

        if lookup_type is 'in':
            final_filters = Q(**{"{}__{}".format(self.name, lookup_type): values})
        else:
            filters = [Q(**{"{}__{}".format(self.name, lookup_type): value}) for value in values]
            final_filters = reduce(lambda a, b: a | b, filters)

        print(final_filters)

        return qs.filter(final_filters)

class ToManyFilter(CommaSeparatedCharMultipleFilter):
    """
    An in filter for a to-many field, where the IN is executed as a subfilter
    e.g. instead of 
    SELECT "iati_activity"."id" FROM "iati_activity" LEFT OUTER JOIN "iati_activityreportingorganisation" as r ON r.activity_id = iati_activity.id  WHERE "r"."ref" IN ('US-USAGOV');
    
    we do:

    SELECT "iati_activity"."id" FROM "iati_activity" WHERE "iati_activity"."id" IN (SELECT U0."activity_id" FROM "iati_activityreportingorganisation" U0 WHERE U0."ref" = 'US-USAGOV');
    """

    def __init__(self, qs=None, fk=None, **kwargs):
        if not qs:
            raise ValueError("qs must be specified")
        if not fk:
            raise ValueError("fk must be specified, that relates back to the main model")

        self.nested_qs = qs
        self.fk = fk

        super(ToManyFilter, self).__init__(**kwargs)

    def filter(self, qs, value):
        if not value: return qs

        print(value)
        # if value:
        #     value = value.split(',')
        
        nested_qs = self.nested_qs.objects.all()
        nested_qs = super(ToManyFilter, self).filter(nested_qs, value)



        # in_filter = Q(**{"{}__in".format(self.name): value})
        # nested_qs = self.nested_qs.objects.all().filter(in_filter).values(self.fk)

        return qs.filter(id__in=nested_qs.values(self.fk))

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
        if not value: return qs

        print(self.nested_filter)
        print(self.nested_filter())

        return qs.filter(id__in=self.nested_filter.filter(qs, value))

