from django.test.client import Client
from django.core.urlresolvers import reverse
import pytest


@pytest.mark.django_db
class TestBasicResources:

    def test_activities_endpoint(self):
        url = reverse('activity-list')
        client = Client()
        client.get(url)
        # should not raise
