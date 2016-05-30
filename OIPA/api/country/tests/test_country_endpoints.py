from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from geodata.factory import geodata_factory


class TestCountryEndpoints(APITestCase):

    def test_countries_endpoint(self):
        url = reverse('countries:country-list')

        msg = 'countries endpoint should be localed at {0}'
        expect_url = '/api/countries/'
        assert url == expect_url, msg.format(expect_url)
        response = self.client.get(url)
        self.assertTrue(status.is_success(response.status_code))

    def test_country_detail_endpoint(self):
        geodata_factory.CountryFactory(code='AA')
        url = reverse('countries:country-detail', args={'AA'})

        msg = 'country detail endpoint should be localed at {0}'
        expect_url = '/api/countries/AA/'
        assert url == expect_url, msg.format(expect_url)
        response = self.client.get(url)
        self.assertTrue(status.is_success(response.status_code))

