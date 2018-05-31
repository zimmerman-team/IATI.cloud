from django.contrib.gis.geos import fromstr
from django.test import TestCase
from mock import MagicMock

from geodata.factory.geodata_factory import CityFactory, CountryFactory
from geodata.importer.city import CityImport
from geodata.models import City, Country

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


class CityImportTestCase(TestCase):
    def setUp(self):
        self.city = CityFactory.build()
        self.city_importer = CityImport()
        self.country = CountryFactory.create(code="UY")

    def test_update_cities(self):

        self.city_importer.get_json_data = MagicMock(return_value=data)
        self.city_importer.update_cities()

        self.assertEqual(1, self.city_importer.get_json_data.call_count)
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
