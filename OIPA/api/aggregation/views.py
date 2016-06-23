from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from django.db.models import Q, F
from api.aggregation.aggregation import aggregate


class AggregationView(GenericAPIView):

    def apply_limit_offset_filters(self, results, page_size, page):
        """
        limit the results to the amount set by page_size

        The results are all queried so this gives at most a small performance boost
        because there's less data to serialize.
        """
        if page_size:

            if not page:
                page = 1

            page_size = int(page_size)
            page = int(page)

            offset = (page * page_size) - page_size
            offset_plus_limit = offset + page_size
            return results[offset:offset_plus_limit]

        return results

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        params = request.query_params

        aggregations = filter(None, params.get('aggregations', "").split(','))
        groupings = filter(None, params.get('group_by', "").split(','))
        orderings = filter(None, params.get('order_by', "").split(','))

        if not len(groupings):
            return Response({'error_message': "Invalid value for mandatory field 'group_by'"})
        elif not len(aggregations):
            return Response({'error_message': "Invalid value for mandatory field 'aggregations'"})

        selected_groupings = filter(
            lambda x: x.query_param in groupings,
            self.allowed_groupings
        )

        selected_aggregations = filter(
            lambda x: x.query_param in aggregations,
            self.allowed_aggregations
        )

        # selected_orderings = filter(
        #     lambda x: x.query_param in orderings or '-' + x.query_param in orderings,
        #     self.allowed_groupings + self.allowed_aggregations
        # )
        selected_orderings = orderings

        result = aggregate(
            queryset,
            request,
            selected_groupings,
            selected_aggregations,
            selected_orderings,
        )

        page_size = params.get('page_size', None)
        page = params.get('page', None)

        result['results'] = self.apply_limit_offset_filters(result['results'], page_size, page)

        return Response(result)


class GroupBy():
    def __init__(self, query_param=None, fields=None, queryset=None, serializer=None, serializer_main_field="code", serializer_fk="pk", serializer_fields=(), extra=None, renamed_fields=None, name_search_field='', renamed_name_search_field=''):
        """
        fields should be a dictionary of field: rendered_field_name
        """

        if None in [query_param, fields]:
            raise ValueError("not all required params were passed")

        self.query_param = query_param
        self.name_search_field = name_search_field

        if renamed_name_search_field:
            self.renamed_name_search_field = renamed_name_search_field
        else:
            self.renamed_name_search_field = self.name_search_field

        if type(fields) is str:
            self.fields = (fields,)
        elif type(fields) is not tuple:
            raise ValueError("fields must be either a string or a tuple of values")
        else:
            self.fields = fields

        if renamed_fields:
            if type(renamed_fields) is str:
                self.renamed_fields = (renamed_fields,)
            elif type(renamed_fields) is not tuple:
                raise ValueError("renamed_fields must be either a string or a tuple of values")
            else:
                if len(renamed_fields) > len(fields):
                    raise ValueError("renamed fields length must be lte to fields length")
                self.renamed_fields = renamed_fields
        else:
            self.renamed_fields = renamed_fields

        self.queryset = queryset
        self.serializer = serializer
        self.serializer_main_field = serializer_main_field
        self.serializer_fk = serializer_fk
        self.serializer_fields = serializer_fields
        self.extra = extra

    def get_renamed_fields(self):
        """
        return a dictionary of (newName, oldName) keys and values
        can be used to annotate the renamed fields
        """

        if self.renamed_fields:
            return { zipped[0]:F(zipped[1]) for zipped in zip(self.renamed_fields, self.fields) }

        return dict()

    def get_fields(self):
        """
        """
        if self.renamed_fields:
            # handle partly renaming
            return self.renamed_fields + self.fields[len(self.renamed_fields):]
        else:
            return self.fields

    def serialize_results(self, l, request):
        """
        given an array of result dictionaries, serialize the result[key]
        this mutates the input list #{l}
        """

        # TODO: Merge serializer results on queryset instead of on the joined result - 2016-04-08
        
        if not self.serializer:
            return l

        # TODO: how do we handle this case? - 2016-04-08
        if len(self.fields) > 1:
            return l

        field = self.get_fields()[0]

        values = map(lambda r: r[field], l)

        queryset = self.queryset.all() \
            .filter(**{"{}__in".format(self.serializer_fk): values})

        data = self.serializer(
            queryset,
            context={
                'request': request,
            },
            many=True,
            fields=self.serializer_fields
        ).data

        # TODO: get serializer main field from serializer? - 2016-04-12

        # TODO: eliminate this expensive step - 2016-04-08
        # data_dict = {str(i.get('code')): i for i in data}
        data_dict = {str(i.get(self.serializer_main_field)): i for i in data}

        result = map(lambda i: merge([i, dict([
            (
                field, 
                data_dict.get(str(i[field]))
            )
            ])
            ]), l)

        return result


class Aggregation():

    def __init__(self, query_param=None, field=None, annotate=None, extra_filter=None, annotate_name=None, extra=None):

        if not (query_param and field and annotate):
            raise ValueError("not all required params were passed")


        if extra_filter and not isinstance(extra_filter, Q):
            raise ValueError("extra_filter must be a django Q() object")

        self.query_param = query_param
        self.field = field
        self.annotate = annotate
        self.annotate_name = annotate_name or field
        self.extra_filter = extra_filter

        self.extra = extra

    def apply_extra_filter(self, queryset):
        if self.extra_filter:
            return queryset.filter(self.extra_filter)
        else:
            return queryset

    def apply_annotation(self, queryset, query_params=None, groupings=None):
        """
        apply the specified annotation to ${queryset}
        """

        if isfunc(self.annotate):
            annotate = self.annotate(query_params, groupings)
        else:
            annotate = self.annotate

        annotation = dict([(self.annotate_name, annotate)])
        return queryset.annotate(**annotation)

# TODO: seems unnescessary - 2016-04-11
class Order:
    def __init__(self, query_param=None, fields=None):
        if not (query_param or field):
            raise ValueError("not all required params were passed")
        
        self.query_param = query_param
        self.fields = fields


def isfunc(obj):
    return hasattr(obj, '__call__')

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

