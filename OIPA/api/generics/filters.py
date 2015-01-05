from rest_framework import filters
from django.db.models.sql.constants import QUERY_TERMS

VALID_LOOKUP_TYPES = sorted(QUERY_TERMS)


class SearchFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        query = request.QUERY_PARAMS.get('q', None)
        if query:
            query_fields = request.QUERY_PARAMS.get('q_fields')
            if query_fields:
                query_fields = query_fields.split(',')
            return queryset.search(query, query_fields)
        return queryset.all()


class FilterField(object):

    def __init__(self, lookup_type=None, field=None):
        assert lookup_type in VALID_LOOKUP_TYPES,\
            'lookup_type in FilterSpecification is invalid'

        self.lookup_type = lookup_type
        self.field = field


class BasicFilter(object):

    @property
    def fields(self):
        return self.Meta.fields

    @property
    def model(self):
        return self.Meta.model

    def __init__(self):

        assert self.fields,\
            'filter_class is declared but no filter_fields'

        # Check that all fields specified in the dictionary
        # have a filters.FilterField object
        unknown_fields = set(self.fields) - set(dir(self))
        assert len(unknown_fields) == 0,\
            'filter_class contains fields that do not exist'

        # When model is specified, check that all FilterField.field
        # are available in the model.
        if self.model is not None:
            model_obj = self.model()
            model_fields = model_obj._meta.get_all_field_names()

            filter_field_model_names = []
            for filter in self.fields:
                filter_field = getattr(self, filter, None)
                filter_field_model_names.append(filter_field.field)

            unknown_model_fields = set(filter_field_model_names) - set(model_fields)
            assert len(unknown_model_fields) == 0,\
                'field does not exist in model'


class BasicFilterBackend(filters.BaseFilterBackend):

    def filter_field_queryset_parameters(self, params=None, filter=None):
        filter = filter()

        to_filter_fields = set(filter.fields) & set(params.keys())

        lookup_parameters = {}
        for field in to_filter_fields:
            filter_field = getattr(filter, field, None)

            lookup_type = filter_field.lookup_type
            field_name = filter_field.field

            if lookup_type == 'in':
                parameter_value = params[field].split(',')
            else:
                parameter_value = params[field]

            lookup_parameters[field_name + '__' + lookup_type] = parameter_value

        return lookup_parameters

    def filter_field_queryset(self, params=None, filter=None, queryset=None):
        queryset_parameters = self.filter_field_queryset_parameters(
            params=params, filter=filter)

        return queryset.filter(**queryset_parameters)

    def filter_queryset(self, request, queryset, view):
        filter_class = getattr(view, 'filter_class', None)

        if filter_class is None:
            return queryset

        queryset = self.filter_field_queryset(
            params=request.QUERY_PARAMS, filter=filter_class, queryset=queryset)

        return queryset
