from mock import MagicMock

from django.contrib.admin.sites import AdminSite
from django.test import TestCase

from geodata.factory.geodata_factory import CountryFactory
from geodata.factory.geodata_factory import RegionFactory
from geodata.models import Country
from geodata.admin_models.country_admin import CountryAdmin


class MockRequest(object):
    pass


class MockSuperUser(object):
    def has_perm(self, perm):
        return True

request = MockRequest()
request.user = MockSuperUser()


class CountryAdminTestCase(TestCase):

    def setUp(self):
        self.site = AdminSite()
        self.country = CountryFactory.create(code="AF")

    def test_get_urls(self):

        country_admin = CountryAdmin(self.country, self.site)
        patterns = []
        for url in country_admin.get_urls():
            patterns.append(url.regex.pattern)

        added_patterns = [
            '^update-polygon/$',
            '^update-country-center/$',
            '^update-alt-names/$',
            '^update-regions/$',
            '^update-country-identifiers/$']

        for pattern in added_patterns:
            self.assertIn(pattern, patterns)

    def test_update_polygon(self):
        country_admin = CountryAdmin(self.country, self.site)
        data = {
            "type": "FeatureCollection","features": [{
                "type": "Feature",
                "id": "AFG",
                "properties": {
                    "name": "Afghanistan",
                    "iso2": "AF"
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[61.210817, 35.650072], [62.230651, 35.270664]]]}},
        ]}
        country_admin.get_json_data = MagicMock(return_value=data)
        country_admin.update_polygon(request)

        self.assertEqual(1, country_admin.get_json_data.call_count)
        self.assertEqual(1, Country.objects.all().count())

        country = Country.objects.all()[0]

        self.assertIsNotNone(country.polygon)
        self.assertEqual(country.code, self.country.code)

    def test_update_country_center(self):
        country_admin = CountryAdmin(self.country, self.site)
        data = {"AF": {"latitude": "42.30", "longitude": "1.30"},}
        country_admin.get_json_data = MagicMock(return_value=data)
        country_admin.update_country_center(request)
        country = Country.objects.all()[0]
        self.assertEqual(country.center_longlat.y, 42.3)
        self.assertEqual(country.center_longlat.x, 1.3)

    def test_update_regions(self):
        country_admin = CountryAdmin(self.country, self.site)
        region = RegionFactory.create(code='689')
        data = [{
            "country_name": "Afghanistan",
            "iso2": "AF",
            "dac_region_code": "689",
        }, ]
        country_admin.get_json_data = MagicMock(return_value=data)

        country_admin.update_regions(request)
        country = Country.objects.all()[0]
        self.assertEqual(country.region, region)

    def test_update_country_identifiers(self):
        country_admin = CountryAdmin(self.country, self.site)
        data = {
            "codemappings":{
                "territorycodes": [
                {
                    "type": "AF",
                    "numeric": 4,
                    "alpha3": "AFG"
                },
        ]}}

        country_admin.get_json_data = MagicMock(return_value=data)
        country_admin.update_country_identifiers(request)
        country = Country.objects.all()[0]

        self.assertEqual(country.numerical_code_un, 4)
        self.assertEqual(country.alpha3, "AFG")

    def test_update_alt_names(self):
        country_admin = CountryAdmin(self.country, self.site)
        data = {"AF": {"alt_name": "Alt AF name"}, }
        country_admin.get_json_data = MagicMock(return_value=data)
        country_admin.update_alt_names(request)

        country = Country.objects.all()[0]

        self.assertEqual(country.alt_name, "Alt AF name")