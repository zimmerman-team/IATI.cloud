from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase


class TestActivityEndpoints(APITestCase):
    def test_activity_aggregations_endpoint(self):
        url = reverse('budgets:budget-aggregations')
        msg = 'budget aggregations endpoint should be located at {0}'
        expect_url = '/api/budgets/aggregations/'
        assert url == expect_url, msg.format(expect_url)
        response = self.client.get(
            expect_url, {
                'group_by': 'sector', 'aggregations': 'count'}, format='json')
        self.assertTrue(status.is_success(response.status_code))
