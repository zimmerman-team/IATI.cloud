from rest_framework import serializers


class DynamicFields(object):

    def __init__(self, *args, **kwargs):
        self.query_field = kwargs.pop('query_field', 'fields')
        self._selected_fields = kwargs.pop('fields', None)
        self.fields_selected = False

        super(DynamicFields, self).__init__(*args, **kwargs)

    def _selected_fields_from_request(self, request):
        selected_fields = []

        query_params = getattr(request, 'query_params', {})
        fields_dict = {k: v for k, v in query_params.items()
                       if k.startswith(self.query_field)}

        if self.query_field in fields_dict:
            fields = fields_dict.pop(self.query_field, [])
            selected_fields = fields.split(',')

        for k, v in fields_dict.items():
            # remove '<query_field>[' and ']'
            field_name = k[(len(self.query_field)+1):-1]

            if field_name in self.fields.keys():
                selected_fields.append(field_name)
                self.fields[field_name].selected_fields = v.split(',')

        return selected_fields

    @property
    def selected_fields(self):
        """
        Returns the selected fields in the DynamicFieldsSerializer.
        """
        request = self.context.get('request')
        view = self.context.get('view')

        if not isinstance(self.parent, DynamicFields):
            if view and self._selected_fields is None:
                fields = getattr(view, 'fields', None)
                if fields:
                    self._selected_fields = fields

            if request:
                fields = self._selected_fields_from_request(request)
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
