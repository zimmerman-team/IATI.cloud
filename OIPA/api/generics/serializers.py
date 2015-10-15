from rest_framework import serializers
from api.generics import utils
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict


class FilteredListSerializer(serializers.ListSerializer):
    """
        Allow filters to be applied in nested ListSerializers.
        Requires context to be passed.
    """

    def __init__(cls, *args, **kwargs):
        cls.filter_class = kwargs.pop('filter_class', ())
        return super(FilteredListSerializer, cls).__init__(*args, **kwargs)

    def to_representation(self, queryset):
        request = self.context.get("request")

        if self.filter_class:
            queryset = self.filter_class(request.query_params, queryset=queryset).qs
        
        return super(FilteredListSerializer, self).to_representation(queryset)

class FilterableModelSerializer(serializers.ModelSerializer):

    @classmethod
    def many_init(cls, *args, **kwargs):
        meta = getattr(cls, 'Meta', None)
        filter_class = getattr(meta, 'filter_class', ())

        kwargs['child'] = cls()
        kwargs['filter_class'] = filter_class
 
        return FilteredListSerializer(*args, **kwargs)

class DynamicFields(object):

    @property
    def is_root_dynamic_fields(self):
        """
        Returns true if the current DynamicFields serializer is the root
        DynamicFields serializer.
        """
        parent = self.parent
        root = self.root
        result = None

        if parent is None:
            return True

        while result is None:
            if root == parent or not hasattr(parent, 'parent'):
                result = True
            if isinstance(parent, DynamicFields):
                result = False
            else:
                parent = parent.parent
        return result

    def __init__(self, *args, **kwargs):
        self.query_field = kwargs.pop('query_field', 'fields')
        self._selected_fields = kwargs.pop('fields', None)
        self.fields_selected = False

        super(DynamicFields, self).__init__(*args, **kwargs)

    def _selected_fields_from_query_params(self, query_params):
        selected_fields = []

        if self.query_field in query_params:
            selected_fields = query_params[self.query_field].split(',')

        fields_dict = utils.get_type_parameters(self.query_field, query_params)
        for k, v in fields_dict.items():
            if k in self.fields.keys():
                selected_fields.append(k)
                self.fields[k].selected_fields = v.split(',')

        return selected_fields

    @property
    def selected_fields(self):
        """
        Returns the selected fields in the DynamicFieldsSerializer.
        """
        query_params = utils.query_params_from_context(self.context)
        view = self.context.get('view')

        if self.is_root_dynamic_fields:
            if view and self._selected_fields is None:
                fields = getattr(view, 'fields', None)
                if fields:
                    self._selected_fields = fields

            if query_params:
                fields = self._selected_fields_from_query_params(query_params)
                if fields:
                    self._selected_fields = fields

        if self._selected_fields and not isinstance(
                self._selected_fields, (list, tuple)):
            raise TypeError(
                'The `fields` option must be a list or tuple. Got %s.' %
                type(self._selected_fields).__name__
            )

        return self._selected_fields

    @selected_fields.setter
    def selected_fields(self, fields):
        self._selected_fields = fields

    def select_fields(self):
        if self.selected_fields is not None:
            keep_fields = set(self.selected_fields)
            all_fields = set(self.fields.keys())
            for field_name in all_fields - keep_fields:
                del self.fields[field_name]

    def to_representation(self, instance):
        if not self.fields_selected:
            self.select_fields()
            self.fields_selected = True
        return super(DynamicFields, self).to_representation(instance)


class DynamicFieldsSerializer(DynamicFields, serializers.Serializer):
    def __init__(self, *args, **kwargs):
        # Instantiate mixin, superclass
        super(DynamicFieldsSerializer, self).__init__(*args, **kwargs)


class DynamicFieldsModelSerializer(DynamicFields, serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        # Instantiate mixin, superclass
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

class DynamicFieldsSerializer(DynamicFields, serializers.Serializer):
    """
    Serializer allowing for dynamic field instantiation
    """

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', ())

        super(DynamicFieldsSerializer, self).__init__(*args, **kwargs)

        if len(fields) > 0:
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    Serializer allowing for dynamic field instantiation
    """

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', ())

        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if len(fields) > 0:
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


# todo: optional remove count or remove this
class NoCountPaginationSerializer(PageNumberPagination):
    """
    PaginationSerializer that removes the count field when specified in the
    query_params.
    """
    def __init__(self, *args, **kwargs):
        super(NoCountPaginationSerializer, self).__init__(*args, **kwargs)
