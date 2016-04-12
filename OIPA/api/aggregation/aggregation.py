
from operator import itemgetter

from django.db.models import Count
from django.db.models import Sum
from django.db.models import Q, F
from django.db.models.functions import Coalesce
from django.db import connection

def apply_annotations(queryset, selected_groupings, selected_aggregations):
    """
    Builds and performs the query, when multiple aggregations were requested it joins the results
    """
    result_dict = None


    #
    # Apply group_by fields and renames
    #

    group_fields = flatten([ grouping.get_fields() for grouping in selected_groupings ])
    rename_annotations = merge([ grouping.get_renamed_fields() for grouping in selected_groupings ])
    group_extras = merge([ grouping.extra for grouping in selected_groupings ])

    eliminate_nulls = {"{}__isnull".format(grouping): False for grouping in group_fields}

    queryset = queryset \
            .extra(select=group_extras) \
            .annotate(**rename_annotations) \
            # .filter(**eliminate_nulls) \

    if len(group_extras) is 0:
        queryset = queryset \
                .filter(**eliminate_nulls) \


    # preparation for aggregation look
    main_group_key = group_fields[0]
    rest_group_keys = group_fields[1:]

    def get_aggregation_queryset(queryset, group_fields, aggregation):

        # TODO: Should queryset be copied here? - 2016-04-07
        next_result = queryset.all()

        # apply any extra aggregation filters if specified
        next_result = aggregation.apply_extra_filter(next_result)

        # apply group_by values() call
        next_result = next_result.values(*group_fields)

        # apply the aggregation annotation
        next_result = aggregation.apply_annotation(next_result)

        return next_result


    aggregation_querysets = [ 
        get_aggregation_queryset(queryset, group_fields, aggregation)
            for aggregation in selected_aggregations 
    ]

    def merge_results(querysets, group_fields):
        """
        Execute the querysets and merge the results into one list of dictionaries
        This method keeps ordering of keys in order of execution of the aggregations
        """

        if len(querysets) is 1:
            return querysets[0]

        first_queryset = querysets[0]
        next_querysets = querysets[1:]

        result_dict = {}

        def get_group_key(item, group_fields):
            """
            Generate a unique group key from fields that are grouped by
            """
            if len(group_fields) is 1:
                return item[group_fields[0]]
            else:
                group_keys = []
                for group_field in group_fields:
                    if isinstance(item[group_field], int):
                        group_keys.append(str(item[group_field]))
                    if isinstance(item[group_field], unicode):
                        group_keys.append(item[group_field].encode('utf-8'))
                return '__'.join(group_keys)

        for item in iter(first_queryset):
            group_key = get_group_key(item, group_fields)
            result_dict[group_key] = item.copy()

        for queryset in next_querysets:
            for item in iter(queryset):
                group_key = get_group_key(item, group_fields)


                # new key not previously seen
                if group_key not in result_dict:
                    result_dict[group_key] = item.copy()
                else:
                    result_dict[group_key] = merge([result_dict[group_key], item.copy()])

        return list(result_dict.values())

    result = merge_results(aggregation_querysets, group_fields)

    return result


def serialize_foreign_keys(result, selected_groupings, request):
    """
    Re-use serializers to show full info of the grouped by items.

    Not all group by keys are serialized, this is based upon the value at _groupings.serializer
    """

    for grouping in selected_groupings:
        """
        Mutate result object for each item in the result[] array
        """
        serializer = grouping.serializer
        serializer_fields = grouping.serializer_fields

        result = grouping.serialize_results(result, request)

    return result

def apply_ordering(result, orderings):
    """
    orders a list by a key

    parameters
    result    - list of results
    orderings - list of order keys
    """

    if len(orderings):
        orderings = reversed(orderings)
        reverse = False

        for order in orderings:
            field = order

            if field[0] == '-':
                reverse = True
                field = field[1:]

            result = sorted(result, key=itemgetter(field), reverse=reverse)

    return result

def apply_group_filters(queryset, selected_groupings, params):
    """
    Filters that are applied only to filter direct visible results as returned
    by the GROUP_BY clause.
    """

    groupings = filter(
        lambda x: x.query_param in params,
        selected_groupings
    )

    for group in groupings:
        main_field = group.fields[0] # the one giving the relation from activity to id of item
        value = params[group.query_param]

        # TODO: We assume here all item filters are IN filters - 2016-03-07
        if isinstance(main_field, str):
            queryset = queryset.filter(**{"{}__in".format(main_field): value.split(',')})

    return queryset

def aggregate(queryset, request, selected_groupings, selected_aggregations, selected_orderings):
    """
        A view can call this function
    """
    # remove any existing ordering
    queryset = queryset.order_by()
    params = request.query_params

    # TODO: just throw exceptions here and catch in view - 2016-04-08
    if not len(selected_groupings):
        return {'error_message': "Invalid value for mandatory field 'group_by'"}
    elif not len(selected_aggregations):
        return {'error_message': "Invalid value for mandatory field 'aggregations'"}

    # filters that reduce the amount of "items" returned in the group_by
    # These filters must be applied directly instead of through "activity id" IN filters
    queryset = apply_group_filters(queryset, selected_groupings, params)

    # from here, queryset is a list
    result = apply_annotations(queryset, selected_groupings, selected_aggregations)

    # TODO: is this correct? - 2016-04-07
    count = len(result)

    # TODO: Can we let db do the ordering? - 2016-04-07
    result = apply_ordering(result, selected_orderings)
    result = serialize_foreign_keys(result, selected_groupings, request)

    return {
        'count': count,
        'results': result
    }

def intersection(list1, list2):
    """
    Return the intersection of two lists
    """
    return list(set(list1) & set(list2))

def flatten(l):
    """
    flatten a list of lists to a single list
    """
    return reduce(lambda x, y: x+y, l)

def merge(l):
    """
    merge a list dictionaries to one dictionary
    """
    if len(l) is 1:
        return l[0]

    result = {}
    for d in l:
        result.update(d)

    return result

