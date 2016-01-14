from mock import MagicMock

from django.contrib.admin.sites import AdminSite
from django.contrib.gis.geos import fromstr
from django.test import TestCase

from geodata.factory.geodata_factory import CityFactory
from geodata.factory.geodata_factory import CountryFactory
from geodata.models import City
from geodata.models import Country
from geodata.admin_models.city_admin import CityAdmin


class MockRequest(object):
    pass


class MockSuperUser(object):
    def has_perm(self, perm):
        return True

request = MockRequest()
request.user = MockSuperUser()

data = {
    "type": "FeatureCollection",
    "crs": {
        "type": "name",
        "properties": {"name": "urn:ogc:def:crs:EPSG::37001"}
    },
    "features": [
        {
            "type": "Feature",
            "properties": {
                "GEONAMEID": 3443013.000000,
                "FEATURECLA": "Admin-0 capital",
                "NAME": "Colonia del Sacramento",
                "NAMEPAR": "name par",
                "NAMEALT": "name alt",
                "NAMEASCII": "ascii name",
                "ISO_A2": "UY",
                "LATITUDE": -34.479999,
                "LONGITUDE": -57.840002
            }
        }
    ]
}


class CityAdminTestCase(TestCase):
    def setUp(self):
        self.city = CityFactory.build()
        self.site = AdminSite()
        self.country = CountryFactory.create(code="UY")

    def test_get_cities_json_data(self):
        ma = CityAdmin(self.city, self.site)
        data = ma.get_cities_json_data()
        self.assertIsInstance(data, dict)

    def test_update_cities(self):
        ma = CityAdmin(self.city, self.site)

        ma.get_cities_json_data = MagicMock(return_value=data)
        ma.update_cities(request)

        self.assertEqual(1, ma.get_cities_json_data.call_count)
        self.assertEqual(1, City.objects.all().count())

        city = City.objects.all()[0]
        country = Country.objects.all()[0]
        longlat = fromstr('POINT(-57.840002 -34.479999)', srid=4326)

        self.assertEqual(city.geoname_id, 3443013)
        self.assertEqual(city.name, "Colonia del Sacramento")
        self.assertEqual(city.namepar, "name par")
        self.assertEqual(city.alt_name, "name alt")
        self.assertEqual(city.ascii_name, "ascii name")
        self.assertEqual(city.country, self.country)
        self.assertEqual(city.location, longlat)
        self.assertEqual(city, country.capital_city)





