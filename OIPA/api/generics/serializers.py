from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.fields import SkipField

from collections import OrderedDict

class XMLMetaMixin(object):
    def to_representation(self, *args, **kwargs):
        representation = super(XMLMetaMixin, self).to_representation(*args, **kwargs)
        if hasattr(self, 'xml_meta'):
            representation.xml_meta = self.xml_meta
        return representation

class SkipNullMixin(object):

    """Don't render null fields"""

    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        ret = OrderedDict()
        fields = self._readable_fields

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            if attribute is None:
                # We skip `to_representation` for `None` values so that
                # fields do not have to explicitly deal with that case.
                continue
            else:
                ret[field.field_name] = field.to_representation(attribute)

        return ret


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

