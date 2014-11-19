import pytest
from django.core.urlresolvers import reverse
from api.tests.endpoint_base import EndpointBase


@pytest.mark.django_db
class TestRegionEndpoints(EndpointBase):

    def test_activities_endpoint(self, client, region):
        url = reverse('region-list')
        response = client.get(url)
        assert response.status_code == 200

    def test_activity_detail_endpoint(self, client, region):
        url = reverse('region-detail', args={'1'})
        response = client.get(url)
        assert response.status_code == 200
