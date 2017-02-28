from django.test import TestCase
import unittest
from mock import MagicMock
from iati.management.commands.set_searchable_activities import *
from iati_codelists.factory import codelist_factory 
from iati.factory import iati_factory
from iati.transaction import factories as transaction_factory


class SearchableActivitiesTestCase(TestCase):
    """
        
    """

    def setUp(self):
        settings.ROOT_ORGANISATIONS = ['GB-1']
        self.command = Command()

        # create 3 activities
        # -one reporting-org GB-1
        # -one GB-1 searchable
        # -one non searchable 

        version = codelist_factory.VersionFactory(code='2.01')
        self.first_activity = iati_factory.ActivityFactory.create(
            iati_identifier='GB-1-1',
            iati_standard_version=version)
        self.second_activity = iati_factory.ActivityFactory.create(
            iati_identifier='GB-CHC-1',
            iati_standard_version=self.first_activity.iati_standard_version)
        self.third_activity = iati_factory.ActivityFactory.create(
            iati_identifier='GB-CHC-2',
            iati_standard_version=self.first_activity.iati_standard_version)
        organisation_type = codelist_factory.OrganisationTypeFactory()
        organisation = iati_factory.OrganisationFactory(
            id="org_id", 
            organisation_identifier="org_id")
        iati_factory.ReportingOrganisationFactory.create(
            ref='GB-1',
            activity=self.first_activity,
            type=organisation_type,
            organisation=organisation
        )
        iati_factory.ReportingOrganisationFactory.create(
            ref='GB-CHC-1',
            activity=self.second_activity,
            type=organisation_type,
            organisation=organisation
        )
        iati_factory.ReportingOrganisationFactory.create(
            ref='GB-CHC-1',
            activity=self.third_activity,
            type=organisation_type,
            organisation=organisation
        )
        transaction = transaction_factory.TransactionFactory.create(
            activity=self.second_activity,
        )
        transaction_provider = transaction_factory.TransactionProviderFactory.create(
            ref = "GB-1",
            normalized_ref = "GB-1",
            provider_activity = self.first_activity,
            provider_activity_ref = "GB-1-1",
            transaction=transaction
        )

    def test_update_searchable_activities(self):
        """
        Test if root organisations projects are set as searchable.
        This tests both update_searchable_activities and set_children_searchable.
        """
        self.command.update_searchable_activities()

        self.first_activity.refresh_from_db()
        self.assertTrue(self.first_activity.is_searchable)

        self.second_activity.refresh_from_db()
        self.assertTrue(self.second_activity.is_searchable)

        self.third_activity.refresh_from_db()
        self.assertFalse(self.third_activity.is_searchable)

