import csv

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from iati.factory import iati_factory
from iati.permissions.factories import OrganisationUserFactory


class TestOrganisationCSVEndpoints(APITestCase):
    c = APIClient()

    def setUp(self):
        user = OrganisationUserFactory.create(user__username='test2')
        self.c.force_authenticate(user.user)

    def test_organisations_csv_endpoint(self):
        url = reverse('organisations:organisation-list')

        msg = 'organisations endpoint should be localed at {0}'
        expect_url = '/api/organisations/'
        if not url == expect_url:
            raise AssertionError(msg.format(expect_url))
        response = self.c.get(url)
        self.assertTrue(status.is_success(response.status_code))

    def test_organisations_csv_endpoint_format(self):
        url = reverse('organisations:organisation-list')
        enpoint_url = "%s?format=csv" % (url)
        response = self.c.get(enpoint_url)
        self.assertEqual(response.status_code, 200)

        response_headers = response._headers
        content_type = response_headers.get('content-type')

        self.assertEqual(content_type[1], 'text/csv; charset=utf-8')

    def test_organisations_csv_endpoint_default_headers(self):
        """test if csv output has default headers."""

        url = reverse('organisations:organisation-list')
        enpoint_url = "%s?format=csv" % url
        default_csv_headers = ['organisation-identifier', 'name/0/narratives']

        response = self.c.get(enpoint_url)
        csv_reader = csv.DictReader(response.content.decode("utf-8").split(
            '\n'))
        csv_headers = csv_reader.fieldnames

        for header in csv_headers:
            self.assertTrue(header in default_csv_headers)

    def test_organisations_csv_endpoint_additional_headers(self):
        organisation = iati_factory.OrganisationFactory()
        iati_factory.OrganisationTotalBudgetFactory(organisation=organisation)

        additional_headers = ['default_currency', 'total_budgets']
        headers_name = {

            'reporting_org': [
                'reporting-org/@ref',
                'reporting-org/@type',
                'reporting-org/@secondary-reporter',
                'reporting-org/narratives',
            ],
            'total_budgets': '0/total_budget/value',
            'recipient_org_budgets': '0/recipient-org-budget/recipient-org/@ref',  # NOQA: E501
            'recipient_region_budgets': '0/recipient-region-budget/recipient-region/@code',  # NOQA: E501
            'recipient_country_budgets': '0/recipient-country-budget/recipient-country/@code',  # NOQA: E501
            'total_expenditures': '0/total-expenditure/value',
            'document_links': '0/document_link/@url',
            'default_currency': 'default-currency/@code'
        }

        url = reverse('organisations:organisation-list')
        endpoint_url = "%s?format=csv&fields=" % url

        for h in additional_headers:
            endpoint_url = endpoint_url + h + ','

        response = self.c.get(endpoint_url[:-1])  # remove last comma
        csv_reader = csv.DictReader(response.content.decode("utf-8").split(
            '\n'))
        csv_headers = csv_reader.fieldnames

        for header in additional_headers:
            self.assertTrue(headers_name.get(header) in csv_headers)

    def test_organisations_csv_endpoint_data(self):
        organisation = iati_factory.OrganisationFactory()
        name_narratives = iati_factory.OrganisationNarrativeFactory(
            related_object=organisation.name,
            content=organisation.primary_name)
        default_csv_headers = ['organisation-identifier', 'name/0/narratives']

        url = reverse('organisations:organisation-list')
        enpoint_url = "%s?format=csv" % url

        response = self.c.get(enpoint_url)
        csv_reader = csv.DictReader(response.content.decode("utf-8").split(
            '\n'))
        for row in csv_reader:
            self.assertEqual(row[default_csv_headers[0]],
                             organisation.organisation_identifier)
            self.assertEqual(row[default_csv_headers[1]],
                             name_narratives.content + ';')
