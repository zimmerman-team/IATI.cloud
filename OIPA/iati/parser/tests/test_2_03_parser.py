###########################################################
# Unit tests for new functionality in IATI v. 2.03 parser #
###########################################################

import datetime
from decimal import Decimal

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
from iati_vocabulary.factory.vocabulary_factory import TagVocabularyFactory


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


class ActivityTagTestCase(TestCase):
    """
    2.03: A new, xml element 'tag' was added for Activity
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
        self.activity = iati_factory.ActivityFactory.create(
            iati_standard_version=current_version
        )

        self.parser_203.register_model('Activity', self.activity)

    def test_activity_tag(self):
        """
        - Tests if '<tag>' xml element is parsed and saved correctly with
          proper attributes and narratives
        - Doesn't test if object is actually saved in the database (the final
          stage), because 'save_all_models()' parser's function is (probably)
          tested separately
        """

        # Create specific XML elements for test case:
        activity_tag_attributes = {
            # Vocabulary is missing:

            # "vocabulary": '1',
            "code": '1',
            'vocabulary-uri': 'http://example.com/vocab.html',
        }

        activity_tag_XML_element = E(
            'tag',
            **activity_tag_attributes
        )

        # CASE 1:
        # 'vocabulary' attr is missing:
        try:
            self.parser_203.iati_activities__iati_activity__tag(
                activity_tag_XML_element)
            self.assertFail()
        except RequiredFieldError as inst:
            self.assertEqual(inst.field, 'vocabulary')
            self.assertEqual(inst.message, 'required attribute missing')

        # 'code' attr is missing:
        activity_tag_attributes['vocabulary'] = '1'
        activity_tag_attributes.pop('code')

        activity_tag_XML_element = E(
            'tag',
            **activity_tag_attributes
        )

        try:
            self.parser_203.iati_activities__iati_activity__tag(
                activity_tag_XML_element)
            self.assertFail()
        except RequiredFieldError as inst:
            self.assertEqual(inst.field, 'code')
            self.assertEqual(inst.message, 'required attribute missing')

        # CASE 2:
        # such TagVocabulary doesn't exist (is not yet created for our tests)
        # AND it's not 99:
        activity_tag_attributes['vocabulary'] = '88'
        activity_tag_attributes['code'] = '1'

        activity_tag_XML_element = E(
            'tag',
            **activity_tag_attributes
        )

        try:
            self.parser_203.iati_activities__iati_activity__tag(
                activity_tag_XML_element)
            self.assertFail()
        except FieldValidationError as inst:
            self.assertEqual(inst.field, 'vocabulary')
            self.assertEqual(inst.message, 'If a vocabulary is not on the '
                                           'TagVocabulary codelist, then the '
                                           'value of 99 (Reporting '
                                           'Organisation) should be declared')

        # CASE 3:
        # our system is missing such TagVocabulary object (but vocabulary attr
        # is correct (99)):
        activity_tag_attributes['vocabulary'] = '99'
        activity_tag_attributes['code'] = '1'

        activity_tag_XML_element = E(
            'tag',
            **activity_tag_attributes
        )

        try:
            self.parser_203.iati_activities__iati_activity__tag(
                activity_tag_XML_element)
            self.asseritFail()
        except FieldValidationError as inst:
            self.assertEqual(inst.field, 'vocabulary')
            self.assertEqual(inst.message, 'not found on the accompanying '
                                           'code list')

        # CASE 4:
        # Create a Vocabulary and remove vocabulary-uri attr:
        fresh_tag_vicabulary = TagVocabularyFactory(code='99')

        # Clear codelist cache (from memory):
        self.parser_203.codelist_cache = {}

        activity_tag_attributes['vocabulary'] = '99'
        activity_tag_attributes['code'] = '1'
        activity_tag_attributes.pop('vocabulary-uri')

        activity_tag_XML_element = E(
            'tag',
            **activity_tag_attributes
        )

        try:
            self.parser_203.iati_activities__iati_activity__tag(
                activity_tag_XML_element)
            self.assertFail()
        except FieldValidationError as inst:
            # self.assertEqual(inst.field, 'vocabulary-uri')
            self.assertEqual(inst.message, "If a publisher uses a vocabulary "
                                           "of 99 (i.e. ‘Reporting "
                                           "Organisation’), then the "
                                           "@vocabulary-uri attribute should "
                                           "also be used")

        # CASE 5:
        # ALL IS GOOD:
        activity_tag_attributes[
            'vocabulary-uri'
        ] = 'http://example.com/vocab.html'

        activity_tag_XML_element = E(
            'tag',
            **activity_tag_attributes
        )

        self.parser_203.iati_activities__iati_activity__tag(
            activity_tag_XML_element)

        activity_tag = self.parser_203.get_model(
            'ActivityTag')

        # Check if CRSChannelCode object is assigned to the participating org
        # (model is not yet saved at this point):
        self.assertEquals(
            activity_tag.activity, self.activity
        )
        self.assertEquals(
            activity_tag.code, activity_tag_attributes['code']
        )
        self.assertEquals(
            activity_tag.vocabulary, fresh_tag_vicabulary
        )
        self.assertEquals(
            activity_tag.vocabulary_uri,
            activity_tag_attributes['vocabulary-uri']
        )

        # Saving models is not tested here:
        self.assertEquals(activity_tag.pk, None)


class RecipientCountryTestCase(TestCase):
    """
    2.03: Content must be a decimal number between 0 and 100 inclusive, WITH
    NO PERCENTAGE SIGN
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
        self.activity = iati_factory.ActivityFactory.create(
            iati_standard_version=current_version
        )

        self.parser_203.register_model('Activity', self.activity)

    def test_recipient_country(self):
        """
        - Tests if '<recipient-country>' xml element is parsed and saved
          correctly with proper attributes and narratives
        - Doesn't test if object is actually saved in the database (the final
          stage), because 'save_all_models()' parser's function is (probably)
          tested separately
        """

        recipient_country_attributes = {
            # "code": '1',
            "country": '1',
            "percentage": '50',
        }

        recipient_country_XML_element = E(
            'recipient-country',
            **recipient_country_attributes
        )

        # CASE 1:
        # 'Code' attr is missing:
        try:
            self.parser_203.iati_activities__iati_activity__recipient_country(
                recipient_country_XML_element)
            self.assertFail()
        except RequiredFieldError as inst:
            self.assertEqual(inst.field, 'code')
            self.assertEqual(inst.message, 'required attribute missing')

        # CASE 2:
        # 'Country' attr is missing:

        recipient_country_attributes = {
            "code": '1',
            # "country": '1',
            "percentage": '50',
        }

        recipient_country_XML_element = E(
            'recipient-country',
            **recipient_country_attributes
        )

        try:
            self.parser_203.iati_activities__iati_activity__recipient_country(
                recipient_country_XML_element)
            self.assertFail()
        except FieldValidationError as inst:
            self.assertEqual(inst.field, 'code')
            self.assertEqual(
                inst.message,
                'not found on the accompanying code list'
            )

        # CASE 3:
        # 'percentage' attr is wrong:

        # let's create Country object so parser doesn't complain anymore:
        country = iati_factory.CountryFactory(code='LTU')

        # Clear cache (from memory):
        self.parser_203.codelist_cache = {}

        recipient_country_attributes = {
            # Code is missing:
            "code": country.code,
            "country": '1',
            "percentage": '50%',
        }

        recipient_country_XML_element = E(
            'recipient-country',
            **recipient_country_attributes
        )

        try:
            self.parser_203.iati_activities__iati_activity__recipient_country(
                recipient_country_XML_element)
            self.assertFail()
        except FieldValidationError as inst:
            self.assertEqual(inst.field, 'percentage')
            self.assertEqual(
                inst.message,
                'percentage value is not valid'
            )

        # CASE 4:
        # all is good:

        recipient_country_attributes = {
            # Code is missing:
            "code": country.code,
            "country": '1',
            "percentage": '50',
        }

        recipient_country_XML_element = E(
            'recipient-country',
            **recipient_country_attributes
        )

        self.parser_203.iati_activities__iati_activity__recipient_country(
            recipient_country_XML_element)

        recipient_country = self.parser_203.get_model(
            'ActivityRecipientCountry')

        # check if everything's saved:

        self.assertEquals(
            recipient_country.country, country
        )
        self.assertEquals(
            recipient_country.activity, self.activity
        )
        self.assertEquals(
            recipient_country.percentage,
            Decimal(recipient_country_attributes['percentage'])
        )

        # Saving models is not tested here:
        self.assertEquals(recipient_country.pk, None)
