import pytest
from django.core.urlresolvers import reverse
from api.tests.endpoint_base import EndpointBase


@pytest.mark.django_db
class TestCityEndpoints(EndpointBase):

    def test_cities_endpoint(self, client, city):
        url = reverse('city-list')
        response = client.get(url)
        assert response.status_code == 200

    def test_city_detail_endpoint(self, client, city):
        url = reverse('city-detail', args={'1'})
        response = client.get(url)
        assert response.status_code == 200
