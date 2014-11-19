import pytest
from django.core.urlresolvers import reverse
from api.tests.endpoint_base import EndpointBase


@pytest.mark.django_db
class TestActivityEndpoints(EndpointBase):

    def test_activities_endpoint(self, client, activity):
        url = reverse('activity-list')
        response = client.get(url)
        assert response.status_code == 200

    def test_activity_detail_endpoint(self, client, activity):
        url = reverse('activity-detail', args={'IATI-0001'})
        response = client.get(url)
        assert response.status_code == 200
