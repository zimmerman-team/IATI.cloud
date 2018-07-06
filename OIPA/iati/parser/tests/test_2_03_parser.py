###########################################################
# Unit tests for new functionality in IATI v. 2.03 parser #
###########################################################

import datetime

# Runs each test in a transaction and flushes database
from django.test import TestCase
from lxml.builder import E

from iati.factory import iati_factory
from iati.parser.exceptions import FieldValidationError, RequiredFieldError
from iati.parser.IATI_2_03 import Parse as Parser_203
from iati.parser.parse_manager import ParseManager
from iati_codelists.factory import codelist_factory
from iati_codelists.factory.codelist_factory import VersionFactory
from iati_synchroniser.factory import synchroniser_factory


class ActivityParticipatingOrganisationTestCase(TestCase):
    """
    2.03: A new, not-required attribute 'crs-channel-code' was added
    """

    def setUp(self):

        # 'Main' XML file for instantiating parser:
        xml_file_attrs = {
            "generated-datetime": datetime.datetime.now().isoformat(),
            "version": '2.03',
        }
        self.iati_203_XML_file = E("iati-activities", **xml_file_attrs)

        dummy_source = synchroniser_factory.DatasetFactory.create(
            name="dataset-2"
        )

        self.parser_203 = ParseManager(
            dataset=dummy_source,
            root=self.iati_203_XML_file,
        ).get_parser()

        self.parser_203.default_lang = "en"

        assert(isinstance(self.parser_203, Parser_203))

        # Version
        current_version = VersionFactory(code='2.03')

        # Related objects:
        self.organisation_role = codelist_factory.OrganisationRoleFactory(
            code='1'
        )
        self.activity = iati_factory.ActivityFactory.create(
            iati_standard_version=current_version
        )

    def test_participating_organisation_crs_channel_code(self):
        """
        - Tests if 'crs-channel-code' attribute is parsed and added correctly
          for <participating-organisation> object.
        - Doesn't test if object is actually saved in the database (the final
          stage), because 'save_all_models()' parser's function is (probably)
          tested separately
        """

        # 1. Create specific XML elements for test case:
        participating_org_attributes = {
            "role": self.organisation_role.code,
            "activity-id": self.activity.iati_identifier,
            # code is invalid:
            'crs-channel-code': 'xxx'
        }

        participating_org_XML_element = E(
            'participating-org',
            **participating_org_attributes
        )

        # 2. Create ParticipatingOrganisation object:
        test_organisation = iati_factory\
            .ParticipatingOrganisationFactory.create(
                ref="Gd-COH-123-participating-org",
                activity=self.activity,
            )

        self.parser_203.register_model('Organisation', test_organisation)

        # crs-channel-code is invalid:
        try:
            self.parser_203.iati_activities__iati_activity__participating_org(
                participating_org_XML_element)
            self.assertFail()
        except RequiredFieldError as inst:
            self.assertEqual(inst.message, 'code is invalid')

        # crs-channel-code not found:
        participating_org_attributes['crs-channel-code'] = '123'

        participating_org_XML_element = E(
            'participating-org',
            **participating_org_attributes
        )

        try:
            self.parser_203.iati_activities__iati_activity__participating_org(
                participating_org_XML_element)
            self.assertFail()
        except FieldValidationError as inst:
            self.assertEqual(
                inst.message, 'not found on the accompanying code list'
            )

        # crs-channel-code is correct:
        crs_object_instance = codelist_factory.CRSChannelCodeFactory(
            code='12345'
        )
        participating_org_attributes[
            'crs-channel-code'
        ] = crs_object_instance.code

        participating_org_XML_element = E(
            'participating-org',
            **participating_org_attributes
        )
        self.parser_203.iati_activities__iati_activity__participating_org(
            participating_org_XML_element)

        participating_organisation = self.parser_203.get_model(
            'ActivityParticipatingOrganisation')

        # Check if CRSChannelCode object is assigned to the participating org
        # (model is not yet saved at this point):
        self.assertEquals(
            participating_organisation.crs_channel_code, crs_object_instance
        )

        # Saving models is not tested here:
        self.assertEquals(participating_organisation.pk, None)
