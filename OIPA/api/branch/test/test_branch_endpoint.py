from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class TestCurrentBranch(APITestCase):
    def test_current_branch_endpoint(self):
        url = reverse('branch:current-branch')
        msg = 'branch endpoit should be located at {0}'
        expected_url = '/api/branch/'
        assert url == expected_url, msg.format(expected_url)
        response = self.client.get(url)
        self.assertTrue(status.is_success(response.status_code))
