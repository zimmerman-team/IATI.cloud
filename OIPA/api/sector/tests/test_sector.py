import pytest
from django.core.urlresolvers import reverse
from api.tests.endpoint_base import EndpointBase


@pytest.mark.django_db
class TestSectorEndpoints(EndpointBase):

    def test_sectors_endpoint(self, client, sector):
        url = reverse('sector-list')
        response = client.get(url)
        assert response.status_code == 200

    def test_sector_detail_endpoint(self, client, sector):
        url = reverse('sector-detail', args={'200'})
        response = client.get(url)
        assert response.status_code == 200
