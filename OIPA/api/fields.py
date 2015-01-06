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
