import json

from django.test import RequestFactory
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from iati.factory import iati_factory
from iati.factory.iati_factory import ActivityFactory
from iati.permissions.factories import OrganisationUserFactory
from iati_synchroniser.factory.synchroniser_factory import PublisherFactory


class TestActivityEndpoints(APITestCase):
    rf = RequestFactory()
    c = APIClient()

    def setUp(self):
        user = OrganisationUserFactory.create(user__username='test1')

        self.c.force_authenticate(user.user)

        self.activity = \
            iati_factory.ActivityFactory.create(iati_identifier='activity_id')

    def test_activities_endpoint(self):
        url = reverse('activities:activity-list')
        expect_url = '/api/activities/'
        msg = 'activities endpoint should be located at {0}'
        assert url == expect_url, msg.format(expect_url)
        response = self.c.get(url)
        self.assertTrue(status.is_success(response.status_code))

    def test_activities_endpoint_by_reporting_organisation(self):
        '''Tests if Activities endpoint works properly when having
        organisation identifier as a query parameter
        '''
        publisher = PublisherFactory()
        organisation = publisher.organisation
        reporting_organisation = iati_factory.ActivityReportingOrganisationFactory(  # NOQA: E501
            organisation=organisation,
            # This is the query param:
            ref=organisation.organisation_identifier
        )

        url = reverse('activities:activity-list')
        endpoint_url = "%s?format=json&reporting_organisation_identifier=%s" % (  # NOQA: E501
            url, reporting_organisation.ref
        )

        response = self.c.get(endpoint_url)
        self.assertEqual(response.status_code, 200)

        resp_data = json.loads(response.content)
        self.assertEqual(resp_data['count'], 1)
        self.assertEqual(
            resp_data['results'][0]['iati_identifier'],
            reporting_organisation.activity.iati_identifier
        )

    def test_activities_endpoint_by_multiple_reporting_organisations(self):
        '''Tests if Activities endpoint works properly when having multiple
        organisation identifiers as a query parameter
        '''
        first_publisher = PublisherFactory()

        first_organisation = first_publisher.organisation
        second_organisation = iati_factory.OrganisationFactory(
            organisation_identifier='different_organisation_ID'
        )

        first_reporting_organisation = iati_factory.ActivityReportingOrganisationFactory(  # NOQA: E501
            organisation=first_organisation,
            # This is the query param:
            ref=first_organisation.organisation_identifier,
            activity=iati_factory.ActivityFactory(
                iati_identifier='A'
            )
        )
        second_reporting_organisation = iati_factory.ActivityReportingOrganisationFactory(  # NOQA: E501
            organisation=second_organisation,
            ref=second_organisation.organisation_identifier,
            activity=iati_factory.ActivityFactory(iati_identifier='B')
        )

        url = reverse('activities:activity-list')
        endpoint_url = "%s?format=json&reporting_organisation_identifier=%s,%s" % (  # NOQA: E501
            url,
            first_reporting_organisation.ref,
            second_reporting_organisation.ref
        )

        response = self.c.get(endpoint_url)
        self.assertEqual(response.status_code, 200)

        resp_data = json.loads(response.content)
        self.assertEqual(resp_data['count'], 2)

        self.assertEqual(
            resp_data['results'][0]['iati_identifier'],
            first_reporting_organisation.activity.iati_identifier
        )

        self.assertEqual(
            resp_data['results'][1]['iati_identifier'],
            second_reporting_organisation.activity.iati_identifier
        )

    def test_activity_detail_endpoint(self):
        url = reverse('activities:activity-detail', args={self.activity.pk})
        msg = 'activity detail endpoint should be located at {0}'
        expect_url = '/api/activities/{}/'.format(self.activity.pk)
        assert url == expect_url, msg.format(expect_url)
        response = self.c.get(url)
        self.assertTrue(status.is_success(response.status_code))

    def test_activity_detail_by_iati_identifier_endpoint(self):
        iati_factory.ActivityFactory.create(iati_identifier='activity_id')
        url = reverse('activities:activity-detail-by-iati-identifier',
                      args={'activity_id'})
        iati_factory.ActivityFactory.create(iati_identifier='activity_id')
        ActivityFactory.create(iati_identifier='activity_id')
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
        url = reverse('activities:activity-transactions',
                      args={self.activity.pk})
        msg = 'activity transactions endpoint should be located at {0}'
        expect_url = \
            '/api/activities/{}/transactions/'.format(self.activity.pk)
        assert url == expect_url, msg.format(expect_url)
        response = self.c.get(url)
        self.assertTrue(status.is_success(response.status_code))
