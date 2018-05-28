from django.test import RequestFactory
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from iati.factory.iati_factory import ActivityFactory
from iati.permissions.factories import OrganisationUserFactory


class TestActivityEndpoints(APITestCase):
    rf = RequestFactory()
    c = APIClient()

    def setUp(self):
        user = OrganisationUserFactory.create(user__username='test1')

        self.c.force_authenticate(user.user)

    def test_activities_endpoint(self):
        url = reverse('activities:activity-list')
        expect_url = '/api/activities/'
        msg = 'activities endpoint should be located at {0}'
        assert url == expect_url, msg.format(expect_url)
        response = self.c.get(url)
        self.assertTrue(status.is_success(response.status_code))

    def test_activity_detail_endpoint(self):
        ActivityFactory.create(iati_identifier='activity_id')
        url = reverse('activities:activity-detail', args={'activity_id'})
        msg = 'activity detail endpoint should be located at {0}'
        expect_url = '/api/activities/activity_id/'
        assert url == expect_url, msg.format(expect_url)
        response = self.c.get(url)
        self.assertTrue(status.is_success(response.status_code))

    def test_activity_aggregations_endpoint(self):
        url = reverse('activities:activity-aggregations')
        msg = 'activity aggregations endpoint should be located at {0}'
        expect_url = '/api/activities/aggregations/'
        assert url == expect_url, msg.format(expect_url)
        response = self.c.get(
            expect_url, {
                'group_by': 'recipient_country',
                'aggregations': 'count'
            }, format='json')
        self.assertTrue(status.is_success(response.status_code))

    def test_transactions_endpoint(self):
        url = reverse('activities:activity-transactions', args={'activity_id'})
        msg = 'activity transactions endpoint should be located at {0}'
        expect_url = '/api/activities/activity_id/transactions/'
        assert url == expect_url, msg.format(expect_url)
        response = self.c.get(url)
        self.assertTrue(status.is_success(response.status_code))
