from django.contrib.gis.geos import Point
from django.test import RequestFactory
from geodata.factory import geodata_factory
from api.city import serializers


class TestCitySerializers:
    request_dummy = RequestFactory().get('/')

    def test_CitySerializer(self):
        city = geodata_factory.CityFactory.build(
            id=0,
            name='Amsterdam',
            location=Point(52.37021, 4.89516),
            geoname_id=2759794,
        )
        serializer = serializers.CitySerializer(
            city,
            context={'request': self.request_dummy}
        )

        assert serializer.data['name'] == city.name,\
            """
            'city.name' should be serialized to a field called 'name'
            """
        assert serializer.data['geoname_id'] == city.geoname_id,\
            """
            'city.geoname_id' should be serialized to a field called
            'geoname_id'
            """
        assert 'location' in serializer.data,\
            """
            a serialized city should contain a field called 'location'
            """
        assert 'url' in serializer.data,\
            """
            a serialized city should contain a field called 'url'
            """
        assert 'country' in serializer.data,\
            """
            a serialized city should contain a field called 'country'
            """
        assert 'is_capital' in serializer.data,\
            """
            a serialized city should contain a field called 'is_capital'
            """
