from django.contrib.gis.geos import Point
from django.test import RequestFactory
from geodata.factory import geodata_factory
from api.country import serializers


class TestCountrySerializers:
    request_dummy = RequestFactory().get('/')

    def test_CountrySerializer(self):
        country = geodata_factory.CountryFactory.build(
            code='NL',
            name='Netherlands',
            alt_name='Nederland',
            language='en',
            dac_country_code=1,
            iso3='NLD',
            alpha3='NLD',
            fips10='FIPS',
            center_longlat=Point(5.45, 52.3),
        )
        serializer = serializers.CountrySerializer(
            country,
            context={'request': self.request_dummy}
        )

        assert serializer.data['code'] == country.code,\
            """
            'country.code' should be serialized to a field called 'code'
            """
        assert serializer.data['name'] == country.name,\
            """
            'country.name' should be serialized to a field called 'name'
            """
        assert serializer.data['numerical_code_un'] == country.numerical_code_un,\
            """
            'country.numerical_code_un' should be serialized to a field called 'numerical_code_un'
            """
        assert serializer.data['name'] == country.name,\
            """
            'country.name' should be serialized to a field called 'name'
            """
        assert serializer.data['alt_name'] == country.alt_name,\
            """
            'country.alt_name' should be serialized to a field called 'alt_name'
            """
        assert serializer.data['language'] == country.language,\
            """
            'country.language' should be serialized to a field called 'language'
            """
        assert serializer.data['dac_country_code'] == country.dac_country_code,\
            """
            'country.dac_country_code' should be serialized to a field called 'dac_country_code'
            """
        assert serializer.data['iso3'] == country.iso3,\
            """
            'country.iso3' should be serialized to a field called 'iso3'
            """
        assert serializer.data['alpha3'] == country.alpha3,\
            """
            'country.alpha3' should be serialized to a field called 'alpha3'
            """
        assert serializer.data['fips10'] == country.fips10,\
            """
            'country.fips10' should be serialized to a field called 'fips10'
            """

        required_fields = (
            'url',
            'capital_city',
            'region',
            'un_region',
            'unesco_region',
            'activities',
            'indicators',
        )
        assertion_msg = "the field '{0}' should be in the serialized country"
        for field in required_fields:
            assert field in serializer.data, assertion_msg.format(field)
