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

    def test_activity_sectors_endpoint(self, client, activitysector):
        url = reverse('activity-sectors', args={'IATI-0001'})
        response = client.get(url)
        assert response.status_code == 200

    def test_participating_orgs_endpoint(self, client, participatingorg):
        url = reverse(
            'activity-participating-organisations',
            args={'IATI-0001'})
        response = client.get(url)
        assert response.status_code == 200

    def test_recipient_countries_endpoint(self, client, recipientcountry):
        url = reverse('activity-recipient-countries', args={'IATI-0001'})
        response = client.get(url)
        assert response.status_code == 200
