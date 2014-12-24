from rest_framework import serializers


class GeometryField(serializers.Field):
    def to_representation(self, obj):
        return {
            'type': 'Point',
            'coordinates': [obj.x, obj.y]
        }
