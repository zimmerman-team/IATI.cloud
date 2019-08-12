import csv

from django.test import RequestFactory
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from iati.factory import iati_factory
from iati.permissions.factories import OrganisationUserFactory


class TestActivityCSVEndpoints(APITestCase):
    rf = RequestFactory()
    c = APIClient()

    def setUp(self):
        user = OrganisationUserFactory.create(user__username='test1')

        self.c.force_authenticate(user.user)

        self.activity = \
            iati_factory.ActivityFactory.create(iati_identifier='activity_id')

    def test_activities_csv_endpoint(self):
        url = reverse('activities:activity-list')
        expect_url = '/api/activities/'
        msg = 'activities endpoint should be located at {0}'
        assert url == expect_url, msg.format(expect_url)
        response = self.c.get(url)
        self.assertTrue(status.is_success(response.status_code))

    def test_activities_csv_endpoint_format(self):

        url = reverse('activities:activity-list')
        endpoint_url = "%s?format=csv" % (  # NOQA: E501
            url
        )

        response = self.c.get(endpoint_url)
        self.assertEqual(response.status_code, 200)

        response_headers = response._headers
        content_type = response_headers.get('content-type')

        self.assertEqual(content_type[1], 'text/csv; charset=utf-8')

    def test_activities_csv_endpoint_default_headers(self):
        """test if csv response has default headers."""

        url = reverse('activities:activity-list')
        endpoint_url = "%s?format=csv" % (  # NOQA: E501
            url
        )
        default_csv_headers = ['activity_id', 'sector_code',
                               'sectors_percentage', 'region', 'country']
        response = self.c.get(endpoint_url)
        csv_reader = csv.DictReader(response.content.decode("utf-8").split(
            '\n'), delimiter=';')
        csv_headers = csv_reader.fieldnames
        header_index = 0
        for header in csv_headers:

            self.assertEqual(header, default_csv_headers[header_index])
            header_index += 1

    def test_activities_csv_endpoint_selectable_headers(self):
        """
        test if csv response actually has requested headers.
        """
        iati_factory.TitleFactory(activity=self.activity)
        iati_factory.DescriptionFactory(activity=self.activity)

        url = reverse('activities:activity-list')
        selectable_headers = ['title', 'descriptions']
        endpoint_url = "%s?format=csv&fields=" % (  # NOQA: E501
            url
        )
        for h in selectable_headers:
            endpoint_url = endpoint_url + h + ','
        response = self.c.get(endpoint_url[:-1])  # remove last comma
        csv_reader = csv.DictReader(response.content.decode("utf-8").split(
            '\n'), delimiter=';')
        csv_headers = csv_reader.fieldnames
        for header in selectable_headers:
            self.assertTrue(header in csv_headers)

    def test_activities_csv_endpoint_data(self):
        """test if the data in csv output is correct"""

        sector = iati_factory.ActivitySectorFactory(activity=self.activity)
        country = iati_factory.ActivityRecipientCountryFactory(
            activity=self.activity)

        url = reverse('activities:activity-list')
        endpoint_url = "%s?format=csv" % (  # NOQA: E501
            url
        )
        default_csv_headers = ['activity_id', 'sector_code',
                               'sectors_percentage', 'region', 'country']
        response = self.c.get(endpoint_url)
        csv_reader = csv.DictReader(response.content.decode("utf-8").split(
            '\n'), delimiter=';')

        for row in csv_reader:
            self.assertEqual(row[default_csv_headers[0]],  # it has ';'
                             self.activity.iati_identifier + ';')
            self.assertEqual(row[default_csv_headers[1]], sector.sector.code
                             + ';')
            self.assertEqual(row[default_csv_headers[2]],
                             str(format(sector.percentage, '.2f'))
                             + ';')
            self.assertEqual(row[default_csv_headers[4]],
                             country.country.code + ';')
