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

    def test_activity_sectors_endpoint(self):
        url = reverse('activities:activity-sectors', args={'activity_id'})

        msg = 'activity sectors endpoint should be localed at {0}'
        expect_url = '/api/activities/activity_id/sectors/'
        assert url == expect_url, msg.format(expect_url)

    def test_participating_orgs_endpoint(self):
        url = reverse(
            'activities:activity-participating-organisations',
            args={'activity_id'})

        msg = 'activity participating-orgs endpoint should be localed at {0}'
        expect_url = '/api/activities/activity_id/participating-orgs/'
        assert url == expect_url, msg.format(expect_url)

    def test_recipient_countries_endpoint(self):
        url = reverse('activities:activity-recipient-countries', args={'activity_id'})

        msg = 'activity recipient countries endpoint should be localed at {0}'
        expect_url = '/api/activities/activity_id/recipient-countries/'
        assert url == expect_url, msg.format(expect_url)
