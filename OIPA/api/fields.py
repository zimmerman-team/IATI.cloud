from rest_framework import serializers


class RootField(serializers.Field):
    def field_to_native(self, obj, field_name):
        return getattr(self.root.object, field_name)
