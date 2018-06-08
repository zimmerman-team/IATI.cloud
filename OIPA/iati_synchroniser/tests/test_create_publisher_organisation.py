from django.test import TestCase

from iati.factory import iati_factory
from iati_organisation.models import Organisation
from iati_synchroniser.create_publisher_organisation import (
    create_publisher_organisation
)
from iati_synchroniser.factory import synchroniser_factory


class CreatePublisherOrganisationTestCase(TestCase):
    """
    Test creation of a organisation on adding a publisher
    """

    def setUp(self):
        iati_factory.LanguageFactory.create(code='en', name='English')
        iati_factory.VersionFactory.create(code='2.02', name='2.02')
        iati_factory.OrganisationTypeFactory.create(
            code='22', name='Multilateral')

    def test_update_or_create_publisher_organisation(self):
        """
        check if dataset is saved as expected
        """

        # setup
        publisher = synchroniser_factory.PublisherFactory.create(
            organisation=None)
        publisher_organization_type = "22"

        # call
        create_publisher_organisation(publisher, publisher_organization_type)

        # prepare
        publisher.refresh_from_db()
        organisation = Organisation.objects.get(
            organisation_identifier=publisher.publisher_iati_id)

        # assert
        self.assertEqual(publisher.publisher_iati_id,
                         organisation.organisation_identifier)
        self.assertEqual(publisher.display_name,
                         organisation.name.narratives.first().content)
        self.assertEqual(publisher_organization_type, organisation.type.code)
        self.assertEqual(publisher.publisher_iati_id,
                         organisation.reporting_org.reporting_org_identifier)
        self.assertEqual(publisher.display_name,
                         organisation.reporting_org.narratives.first().content)
