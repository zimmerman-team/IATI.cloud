from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from geodata.factory import geodata_factory


class TestRegionEndpoints(APITestCase):

    def test_regions_endpoint(self):
        url = reverse('regions:region-list')

        msg = 'regions endpoint should be localed at {0}'
        expect_url = '/api/regions/'
        assert url == expect_url, msg.format(expect_url)
        response = self.client.get(url)
        self.assertTrue(status.is_success(response.status_code))

    def test_region_detail_endpoint(self):
        geodata_factory.RegionFactory.create(code='998')
        url = reverse('regions:region-detail', args={'998'})

        msg = 'region detail endpoint should be localed at {0}'
        expect_url = '/api/regions/998/'
        assert url == expect_url, msg.format(expect_url)
        response = self.client.get(url)
        self.assertTrue(status.is_success(response.status_code))
