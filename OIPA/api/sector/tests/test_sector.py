import pytest
from django.core.urlresolvers import reverse
from api.tests.endpoint_base import EndpointBase
from rest_framework import status


@pytest.mark.django_db
class TestSectorEndpoints(EndpointBase):

    def test_sectors_endpoint(self, client, sector):
        url = reverse('sector-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK, \
            'response.status_code should be {expected}'.format(
                expected=status.HTTP_200_OK)

    def test_sector_detail_endpoint(self, client, sector):
        url = reverse('sector-detail', args={'200'})
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK, \
            'response.status_code should be {expected}'.format(
                expected=status.HTTP_200_OK)
