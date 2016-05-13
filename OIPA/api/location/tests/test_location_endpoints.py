from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from iati.factory import iati_factory


class TestLocationEndpoints(APITestCase):
    def test_locations_endpoint(self):
        url = reverse('locations:location-list')
        expect_url = '/api/locations/'
        assert url == expect_url, msg.format('locations endpoint should be located at {0}')
        response = self.client.get(url)
        self.assertTrue(status.is_success(response.status_code))

    def test_location_detail_endpoint(self):
        iati_factory.LocationFactory.create(id=1)
        url = reverse('locations:location-detail', args={'1'})
        msg = 'location detail endpoint should be located at {0}'
        expect_url = '/api/locations/1/'
        assert url == expect_url, msg.format(expect_url)
        response = self.client.get(url)
        self.assertTrue(status.is_success(response.status_code))

