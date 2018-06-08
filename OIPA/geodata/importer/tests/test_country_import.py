from django.test import TestCase
from mock import MagicMock

from geodata.factory.geodata_factory import CountryFactory, RegionFactory
from geodata.importer.country import CountryImport
from geodata.models import Country


class CountryImportTestCase(TestCase):

    def setUp(self):
        self.country_import = CountryImport()
        self.country = CountryFactory.create(code="AF")

    def test_update_polygon(self):

        data = {
            "type": "FeatureCollection", "features": [{
                "type": "Feature",
                "id": "AFG",
                "properties": {
                    "name": "Afghanistan",
                    "iso2": "AF"
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [[61.210817, 35.650072], [62.230651, 35.270664]]
                    ]}},
            ]}
        self.country_import.get_json_data = MagicMock(return_value=data)
        self.country_import.update_polygon()

        self.assertEqual(1, self.country_import.get_json_data.call_count)
        self.assertEqual(1, Country.objects.all().count())
        country = Country.objects.all()[0]

        self.assertIsNotNone(country.polygon)
        self.assertEqual(country.code, self.country.code)

    def test_update_country_center(self):
        data = {"AF": {"latitude": "42.30", "longitude": "1.30"}, }
        self.country_import.get_json_data = MagicMock(return_value=data)
        self.country_import.update_country_center()
        country = Country.objects.all()[0]
        self.assertEqual(country.center_longlat.y, 42.3)
        self.assertEqual(country.center_longlat.x, 1.3)

    def test_update_regions(self):
        region = RegionFactory.create(code='689')
        data = [{
            "country_name": "Afghanistan",
            "iso2": "AF",
            "dac_region_code": "689",
        }, ]
        self.country_import.get_json_data = MagicMock(return_value=data)
        self.country_import.update_regions()
        country = Country.objects.all()[0]
        self.assertEqual(country.region, region)
