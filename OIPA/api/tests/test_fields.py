from django.contrib.gis.geos import Point
from django.test import TestCase

from api.fields import GeometryField


class TestFields(TestCase):
    def test_GeometryField(self):
        point = Point(0, 25)
        field = GeometryField()
        result = field.to_representation(point)
        assert result['type'] == 'Point'
        assert result['coordinates'] == [0.0, 25.0]
