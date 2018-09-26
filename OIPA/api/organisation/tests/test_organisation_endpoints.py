import datetime

from django.test import TestCase
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType

from rest_framework.test import APIClient

from iati_codelists.models import Version, Language, FileFormat, \
    DocumentCategory, DocumentCategoryCategory
from iati_organisation.models import Organisation, OrganisationName, \
    OrganisationNarrative, OrganisationDocumentLink, \
    OrganisationDocumentLinkCategory


class TestOrganisationEndpoints(TestCase):

    def test_organisations_endpoint(self):
        url = reverse('organisations:organisation-list')

        msg = 'organisations endpoint should be localed at {0}'
        expect_url = '/api/organisations/'
        assert url == expect_url, msg.format(expect_url)

    def test_organisation_detail_endpoint(self):
        url = reverse('organisations:organisation-detail',
                      args={'organisation-id'})

        msg = 'organisation list endpoint should be localed at {0}'
        expect_url = '/api/organisations/organisation-id/'
        assert url == expect_url, msg.format(expect_url)

    def test_reported_activities_endpoint(self):
        url = reverse(
            'organisations:organisation-reported-activities', args={'code'})

        msg = 'organisation-reported-activities should be located at {0}'
        expect_url = '/api/organisations/code/reported-activities/'
        assert url == expect_url, msg.format(expect_url)

    def test_participated_activities_endpoint(self):
        url = reverse(
            'organisations:organisation-participated-activities',
            args={'code'}
        )

        msg = 'organisation-participated-activities should be located at {0}'
        expect_url = '/api/organisations/code/participated-activities/'
        assert url == expect_url, msg.format(expect_url)


class TestOrganisationFileEndpoints(TestCase):

    def test_organisation_file_document_link_list_url_is_ok(self):
        url = reverse(
            'organisations:organisation-file-organisation-document-link-list',
            kwargs={'organisation_identifier': 'organisation-identifier'}
        )

        msg = 'organisation-document-link-list ' \
              'should be located at {0}'
        expect_url = '/api/organisations/organisation-file' \
                     '/organisation-identifier' \
                     '/organisation-document-link-list/'
        assert url == expect_url, msg.format(expect_url)

    def test_organisation_file_document_link_list_endpoint_result(self):
        # Version
        version = Version(code='2.03')
        version.save()

        # Language
        language = Language(code='en', name='English')
        language.save()

        # Organisation
        organisation_identifier = 'test-org'
        organisation = Organisation(
            organisation_identifier=organisation_identifier,
            normalized_organisation_identifier='test-org',
            iati_standard_version=version,
            primary_name='Test Primary Name')
        organisation.save()

        # Organisation Name
        organisation_name = OrganisationName(organisation=organisation)
        organisation_name.save()

        # Organisation Narrative
        OrganisationNarrative(
            organisation=organisation,
            content_type=ContentType.objects.get_for_model(organisation_name),
            object_id=organisation_name.id,
            language=language,
            content='Test Content').save()

        # File Format
        file_format = FileFormat(code='application/http', name='URL')
        file_format.save()

        # Organisation Document Link
        organisation_document_link = OrganisationDocumentLink(
            organisation=organisation,
            url='https://www.test.com',
            file_format=file_format,
            language=language,
            iso_date=datetime.datetime.strptime('2018-01-01', '%Y-%m-%d'))
        organisation_document_link.save()

        # DocumentCategoryCategory
        document_category_category = DocumentCategoryCategory(
            code='B', name='Organisation Level')
        document_category_category.save()

        # Document Category
        document_category = DocumentCategory(
            code='B01', name='Organisation Web URL',
            category=document_category_category)
        document_category.save()

        # Organisation Document Link Category
        organisation_document_link_category = \
            OrganisationDocumentLinkCategory(
                document_link=organisation_document_link,
                category=document_category)
        organisation_document_link_category.save()

        # API client
        client = APIClient()

        # URL endpoijnt organisation dopcument links
        url = reverse(
            'organisations:organisation-file-organisation-document-link-list',
            kwargs={'organisation_identifier': organisation_identifier})

        # Get response from client
        response = client.get(path=url)

        self.assertEqual(
            organisation_document_link.url, 'https://www.test.com')
