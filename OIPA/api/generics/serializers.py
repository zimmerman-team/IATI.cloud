from rest_framework import serializers


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        selected_fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if selected_fields is not None:
            keep_fields = set(selected_fields)
            all_fields = set(self.fields.keys())
            for field_name in all_fields - keep_fields:
                del self.fields[field_name]
