import pytest
from django.core.urlresolvers import reverse
from api.tests.endpoint_base import EndpointBase
from rest_framework import status


@pytest.mark.django_db
class TestCityEndpoints(EndpointBase):

    def test_cities_endpoint(self, client, city):
        url = reverse('city-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK, \
            'response.status_code should be {expected}'.format(
                expected=status.HTTP_200_OK)

    def test_city_detail_endpoint(self, client, city):
        url = reverse('city-detail', args={'1'})
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK, \
            'response.status_code should be {expected}'.format(
                expected=status.HTTP_200_OK)
