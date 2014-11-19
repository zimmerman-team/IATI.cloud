from django.test.client import Client
from django.core.urlresolvers import reverse
import pytest


@pytest.mark.django_db
class TestActivityEndpoints:

    def test_activities_endpoint(self):
        url = reverse('activity-list')
        client = Client()
        response = client.get(url)
        assert response.status_code == 200
