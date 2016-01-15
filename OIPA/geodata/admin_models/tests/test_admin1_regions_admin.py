from mock import MagicMock

from django.contrib.admin.sites import AdminSite
from django.test import TestCase

from geodata.factory.geodata_factory import CountryFactory
from geodata.factory.geodata_factory import Adm1RegionFactory
from geodata.models import Adm1Region
from geodata.admin_models.admin1region_admin import Adm1RegionAdmin


class MockRequest(object):
    pass


class MockSuperUser(object):
    def has_perm(self, perm):
        return True

request = MockRequest()
request.user = MockSuperUser()


class Adm1RegionAdminTestCase(TestCase):

    def setUp(self):
        self.site = AdminSite()
        self.country = CountryFactory.create(code="AF")
        self.adm1_region = Adm1RegionFactory.build()

    def test_get_urls(self):

        region_admin = Adm1RegionAdmin(self.adm1_region, self.site)
        patterns = []
        for url in region_admin.get_urls():
            patterns.append(url.regex.pattern)

        added_patterns = [
            '^update-adm1-regions/$',
        ]

        for pattern in added_patterns:
            self.assertIn(pattern, patterns)

    def test_import_region_center(self):
        region_admin = Adm1RegionAdmin(self.adm1_region, self.site)
        data = {
            "type": "FeatureCollection",
            "features": [
            {
                "type": "Feature",
                "properties": {
                    "adm1_code": "ABW-5150",
                    "OBJECTID_1": 3604,
                    "diss_me": 5150,
                    "adm1_cod_1": "ABW-5150",
                    "iso_3166_2": "AW-",
                    "wikipedia": "",
                    "iso_a2": "AF",
                    "adm0_sr": 3,
                    "name": "State in AF",
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[-69.996938, 12.577582], [-69.936391, 12.531724], ]]
                }
            }]
        }

        region_admin.get_json_data = MagicMock(return_value=data)
        region_admin.update_adm1_regions(request)
        adm1_region = Adm1Region.objects.all()[0]
        self.assertEqual(adm1_region.country.code, 'AF')
        self.assertEqual(adm1_region.name, "State in AF")
        self.assertIsNotNone(adm1_region.polygon)

