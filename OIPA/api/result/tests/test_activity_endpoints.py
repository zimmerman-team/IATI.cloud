from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class TestResultEndpoints(APITestCase):

    def test_result_aggregations_endpoint(self):
        url = reverse('results:result-aggregations')
        msg = 'result aggregations endpoint should be located at {0}'
        expect_url = '/api/results/aggregations/'
        assert url == expect_url, msg.format(expect_url)
        response = self.client.get(
            expect_url, {
                'group_by': 'result_indicator_title',
                'aggregations': 'actual'
            }, format='json')
        self.assertTrue(status.is_success(response.status_code))
