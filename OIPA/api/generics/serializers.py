from rest_framework import serializers
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

            if attribute in [None, '']:
                # We skip `to_representation` for `None` values so that
                # fields do not have to explicitly deal with that case.
                continue

            # check for the case where source="*" is passed
            # if all fields are null in that field, result will be an empty dictionary
            elif instance == attribute:
                result = field.to_representation(attribute)

                if not bool(result): 
                    continue
                else:
                    ret[field.field_name] = result

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

            if 'all' in allowed:
                return

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

            if 'all' in allowed:
                return

            for field_name in existing - allowed:
                self.fields.pop(field_name)


class ModelSerializerNoValidation(DynamicFieldsModelSerializer):
    """
    Serializer with no validation
    """

    def __init__(self, *args, **kwargs):
        kwargs.pop('required', None)
        super(ModelSerializerNoValidation, self).__init__(required=False, *args, **kwargs)


class SerializerNoValidation(DynamicFieldsSerializer):
    """
    Serializer with no validation
    """

    def __init__(self, *args, **kwargs):
        kwargs.pop('required', None)
        kwargs.pop('allow_null', None)
        kwargs.pop('allow_blank', None)
        super(SerializerNoValidation, self).__init__(required=False, allow_null=True, *args, **kwargs)
