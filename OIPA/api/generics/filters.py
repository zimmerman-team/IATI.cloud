from rest_framework import filters
from django.db.models.sql.constants import QUERY_TERMS
from django_filters import CharFilter

VALID_LOOKUP_TYPES = sorted(QUERY_TERMS)


class SearchFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        query = request.query_params.get('q', None)
        if query:
            query_fields = request.query_params.get('q_fields')
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

    @property
    def lookup_parameter(self):
        return self.field + '__' + self.lookup_type


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

    def lookup_parameters(self, params):
        to_filter_fields = set(self.fields) & set(params.keys())

        lookup_parameters = {}
        for field in to_filter_fields:
            filter_field = getattr(self, field, None)

            if filter_field.lookup_type == 'in':
                parameter_value = params[field].split(',')
            else:
                parameter_value = params[field]

            lookup_parameters[filter_field.lookup_parameter] = parameter_value

        return lookup_parameters

    def filter_queryset(self, queryset, params):
        queryset_parameters = self.lookup_parameters(params)

        return queryset.filter(**queryset_parameters)


class BasicFilterBackend(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        filter_class = getattr(view, 'filter_class', None)

        if filter_class is None:
            return queryset

        filter_class = filter_class()
        queryset = filter_class.filter_queryset(
            queryset=queryset,
            params=request.query_params
            )

        return queryset


class CommaSeparatedCharFilter(CharFilter):

    def filter(self, qs, value):

        if value:
            value = value.split(',')

        return super(CommaSeparatedCharFilter, self).filter(qs, value)