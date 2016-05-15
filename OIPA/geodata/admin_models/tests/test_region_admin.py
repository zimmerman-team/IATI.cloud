from mock import MagicMock

from django.contrib.admin.sites import AdminSite
from django.test import TestCase

from geodata.factory.geodata_factory import RegionFactory
from geodata.models import Region
from geodata.admin_models.region_admin import RegionAdmin


class MockRequest(object):
    pass


class MockSuperUser(object):
    def has_perm(self, perm):
        return True

request = MockRequest()
request.user = MockSuperUser()


class RegionAdminTestCase(TestCase):

    def setUp(self):
        self.site = AdminSite()
        self.region = RegionFactory.create(code='689')

    def test_get_urls(self):

        region_admin = RegionAdmin(self.region, self.site)
        patterns = []
        for url in region_admin.get_urls():
            patterns.append(url.regex.pattern)

        added_patterns = ['^update-region-center/$']

        for pattern in added_patterns:
            self.assertIn(pattern, patterns)

    def test_import_region_center(self):
        region_admin = RegionAdmin(self.region, self.site)
        data = {
            "689": {"latitude": "38.526682", "longitude": "69.697266"},
        }
        region_admin.get_json_data = MagicMock(return_value=data)

        region_admin.update_region_center(request)
        region = Region.objects.all()[0]
        self.assertEqual(region.center_longlat.y, 38.526682)
        self.assertEqual(region.center_longlat.x, 69.697266)
