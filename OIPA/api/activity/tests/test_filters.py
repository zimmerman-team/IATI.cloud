from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from iati.factory.iati_factory import ActivityFactory, OtherIdentifierFactory


class ActivityFiltersTestCase(APITestCase):

    def setUp(self):
        self.first_activity = ActivityFactory(
            iati_identifier='XM-DAC-41304-201NEP1000'
        )

        self.first_other_identifier = OtherIdentifierFactory(
            activity=self.first_activity,
            identifier='AAA'
        )

    def test_other_identifier_filter_single_identifier(self):
        url = reverse('activities:activity-list')

        response = self.client.get(url)
        response = self.client.get(
            url, {
                'other_identifier': self.first_other_identifier.identifier,
            }, format='json'
        )

        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(
            response.data['results'][0]['iati_identifier'],
            self.first_activity.iati_identifier
        )

    def test_other_identifier_filter_multiple_identifiers(self):
        # Let's create more activities:
        self.second_activity = ActivityFactory(
            iati_identifier='XM-DAC-41304-170GLO4038'
        )

        self.second_other_identifier = OtherIdentifierFactory(
            activity=self.second_activity,
            identifier='BBB'
        )

        url = reverse('activities:activity-list')

        response = self.client.get(url)
        response = self.client.get(
            url, {
                'other_identifier': '%s,%s' % (
                    self.first_other_identifier.identifier,
                    self.second_other_identifier.identifier
                )
            }, format='json'
        )

        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(
            response.data['results'][0]['iati_identifier'],
            self.first_activity.iati_identifier
        )
        self.assertEqual(
            response.data['results'][1]['iati_identifier'],
            self.second_activity.iati_identifier
        )
