import django.utils.http
from rest_framework import serializers
import json


class GeometryField(serializers.Field):
    def to_representation(self, obj):
        return {
            'type': 'Point',
            'coordinates': [obj.x, obj.y]
        }


class JSONField(serializers.Field):
    def to_representation(self, obj):
        return json.loads(obj)


class EncodedHyperlinkedIdentityField(
        serializers.HyperlinkedIdentityField):

    def get_url(self, obj, view_name, request, format):
        if obj.pk is None:
            return None
        lookup_value = getattr(obj, self.lookup_field)
        quoted_lookup_value = django.utils.http.urlquote(lookup_value)

        kwargs = {self.lookup_url_kwarg: quoted_lookup_value}
        return self.reverse(
            view_name, kwargs=kwargs, request=request, format=format)
