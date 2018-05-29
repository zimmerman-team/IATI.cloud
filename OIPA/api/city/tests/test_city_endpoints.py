from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from geodata.factory import geodata_factory


class TestCityEndpoints(APITestCase):

    def test_cities_endpoint(self):
        url = reverse('cities:city-list')

        msg = 'cities endpoint should be localed at {0}'
        expect_url = '/api/cities/'
        assert url == expect_url, msg.format(expect_url)
        response = self.client.get(url)
        self.assertTrue(status.is_success(response.status_code))

    def test_city_detail_endpoint(self):
        geodata_factory.CityFactory.create(id=1)
        url = reverse('cities:city-detail', args={'1'})

        msg = 'city detail endpoint should be localed at {0}'
        expect_url = '/api/cities/1/'
        assert url == expect_url, msg.format(expect_url)
        response = self.client.get(url)
        self.assertTrue(status.is_success(response.status_code))
