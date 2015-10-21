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

class DynamicFieldsSerializer(serializers.Serializer):
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
