from django.test import TestCase
from django.core.urlresolvers import reverse


class TestActivityEndpoints(TestCase):
    def test_activities_endpoint(self):
        url = reverse('activities:activity-list')

        msg = 'activities endpoint should be localed at {0}'
        expect_url = '/api/activities/'
        assert url == expect_url, msg.format(expect_url)

    def test_activity_detail_endpoint(self):
        url = reverse('activities:activity-detail', args={'activity_id'})

        msg = 'activity detail endpoint should be localed at {0}'
        expect_url = '/api/activities/activity_id/'
        assert url == expect_url, msg.format(expect_url)

    def test_activity_aggregations_endpoint(self):
        url = reverse('activities:activity-aggregations')

        msg = 'activity aggregations endpoint should be localed at {0}'
        expect_url = '/api/activities/aggregations/'
        assert url == expect_url, msg.format(expect_url)

    def test_transactions_endpoint(self):
        url = reverse('activities:activity-transactions', args={'activity_id'})

        msg = 'activity transactions endpoint should be localed at {0}'
        expect_url = '/api/activities/activity_id/transactions/'
        assert url == expect_url, msg.format(expect_url)
