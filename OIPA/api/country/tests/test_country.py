import pytest
from django.core.urlresolvers import reverse
from api.tests.endpoint_base import EndpointBase
from rest_framework import status


@pytest.mark.django_db
class TestRegionEndpoints(EndpointBase):

    def test_countries_endpoint(self, client, country):
        url = reverse('country-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK, \
            'response.status_code should be {expected}'.format(
                expected=status.HTTP_200_OK)

    def test_country_detail_endpoint(self, client, country):
        url = reverse('country-detail', args={'AD'})
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK, \
            'response.status_code should be {expected}'.format(
                expected=status.HTTP_200_OK)
