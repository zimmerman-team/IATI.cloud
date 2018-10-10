###########################################################
# Unit tests for new functionality in IATI v. 2.03 parser #
###########################################################

import datetime
from decimal import Decimal

# Runs each test in a transaction and flushes database
from django.test import TestCase
from lxml.builder import E

from iati.factory import iati_factory
from iati.parser.exceptions import (
    FieldValidationError, IgnoredVocabularyError, RequiredFieldError
)
from iati.parser.IATI_2_03 import Parse as Parser_203
from iati.parser.parse_manager import ParseManager
from iati.transaction.factories import TransactionFactory
from iati_codelists.factory import codelist_factory
from iati_codelists.factory.codelist_factory import VersionFactory
from iati_synchroniser.factory import synchroniser_factory
from iati_vocabulary.factory.vocabulary_factory import (
    AidTypeVocabularyFactory, RegionVocabularyFactory, SectorVocabularyFactory,
    TagVocabularyFactory
)


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

        assert (isinstance(self.parser_203, Parser_203))

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
        test_organisation = iati_factory \
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
        self.assertEqual(
            participating_organisation.crs_channel_code, crs_object_instance
        )

        # Saving models is not tested here:
        self.assertEqual(participating_organisation.pk, None)


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

        assert (isinstance(self.parser_203, Parser_203))

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
        self.assertEqual(
            activity_tag.activity, self.activity
        )
        self.assertEqual(
            activity_tag.code, activity_tag_attributes['code']
        )
        self.assertEqual(
            activity_tag.vocabulary, fresh_tag_vicabulary
        )
        self.assertEqual(
            activity_tag.vocabulary_uri,
            activity_tag_attributes['vocabulary-uri']
        )

        # Saving models is not tested here:
        self.assertEqual(activity_tag.pk, None)


class RecipientCountryTestCase(TestCase):
    """
    2.03: 'percentage' attribute must be a decimal number between 0 and 100
    inclusive, WITH NO PERCENTAGE SIGN
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

        assert (isinstance(self.parser_203, Parser_203))

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

        self.assertEqual(
            recipient_country.country, country
        )
        self.assertEqual(
            recipient_country.activity, self.activity
        )
        self.assertEqual(
            recipient_country.percentage,
            Decimal(recipient_country_attributes['percentage'])
        )

        # Saving models is not tested here:
        self.assertEqual(recipient_country.pk, None)


class RecipientRegionTestCase(TestCase):
    """
    2.03: 'percentage' attribute must be a decimal number between 0 and 100
    inclusive, WITH NO PERCENTAGE SIGN
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

        assert (isinstance(self.parser_203, Parser_203))

        # Version
        current_version = VersionFactory(code='2.03')

        # Related objects:
        self.activity = iati_factory.ActivityFactory.create(
            iati_standard_version=current_version
        )

        self.parser_203.register_model('Activity', self.activity)

    def test_recipient_region(self):
        """
        - Tests if '<recipient-region>' xml element is parsed and saved
          correctly with proper attributes and narratives
        - Doesn't test if object is actually saved in the database (the final
          stage), because 'save_all_models()' parser's function is (probably)
          tested separately
        """

        recipient_region_attributes = {
            # "code": '1',
        }

        recipient_region_XML_element = E(
            'recipient-region',
            **recipient_region_attributes
        )

        # CASE 1:
        # 'Code' attr is missing:
        try:
            self.parser_203.iati_activities__iati_activity__recipient_region(
                recipient_region_XML_element)
            self.assertFail()
        except RequiredFieldError as inst:
            self.assertEqual(inst.model, 'recipient-region')
            self.assertEqual(inst.field, 'code')
            self.assertEqual(inst.message, 'code is unspecified or invalid')

        # CASE 2:
        # Vocabulary not found:

        recipient_region_attributes = {
            "code": '222',
        }

        recipient_region_XML_element = E(
            'recipient-region',
            **recipient_region_attributes
        )

        try:
            self.parser_203.iati_activities__iati_activity__recipient_region(
                recipient_region_XML_element)
            self.assertFail()
        except RequiredFieldError as inst:
            self.assertEqual(inst.model, 'recipient-region')
            self.assertEqual(inst.field, 'vocabulary')
            self.assertEqual(
                inst.message, 'not found on the accompanying code list'
            )

        # CASE 3:
        # Region not found (when code attr == 1):

        # Create Vocabulary obj:
        vocabulary = RegionVocabularyFactory(code=1)

        # Clear codelist cache (from memory):
        self.parser_203.codelist_cache = {}

        recipient_region_attributes = {
            "code": '1',
            "vocabulary": str(vocabulary.code),
        }

        recipient_region_XML_element = E(
            'recipient-region',
            **recipient_region_attributes
        )

        try:
            self.parser_203.iati_activities__iati_activity__recipient_region(
                recipient_region_XML_element)
            self.assertFail()
        except FieldValidationError as inst:
            self.assertEqual(inst.model, 'recipient-region')
            self.assertEqual(inst.field, 'code')
            self.assertEqual(
                inst.message,
                "not found on the accompanying code list"
            )

        # CASE 4:
        # Region not found (when code attr is differnt):

        # Update Vocabulary obj:
        vocabulary.code = 222
        vocabulary.save()

        # Clear codelist cache (from memory):
        self.parser_203.codelist_cache = {}

        recipient_region_attributes = {
            "code": '1',
            "vocabulary": str(vocabulary.code),
        }

        recipient_region_XML_element = E(
            'recipient-region',
            **recipient_region_attributes
        )

        try:
            self.parser_203.iati_activities__iati_activity__recipient_region(
                recipient_region_XML_element)
            self.assertFail()
        except IgnoredVocabularyError as inst:
            self.assertEqual(inst.model, 'recipient-region')
            self.assertEqual(inst.field, 'code')
            self.assertEqual(
                inst.message, 'code is unspecified or invalid'
            )

        # CASE 5:
        # percentage is wrong:

        # Update Vocabulary obj:
        vocabulary.code = 1
        vocabulary.save()

        # Create Region obj:
        region = iati_factory.RegionFactory()

        # Clear codelist cache (from memory):
        self.parser_203.codelist_cache = {}

        recipient_region_attributes = {
            "code": region.code,
            "vocabulary": str(vocabulary.code),
            "percentage": '100%'
        }

        recipient_region_XML_element = E(
            'recipient-region',
            **recipient_region_attributes
        )

        try:
            self.parser_203.iati_activities__iati_activity__recipient_region(
                recipient_region_XML_element)
            self.assertFail()
        except FieldValidationError as inst:
            # self.assertEqual(inst.field, 'percentage')
            self.assertEqual(
                inst.message,
                'percentage value is not valid'
            )

        # CASE 6:
        # All is good:

        # Refresh related object so old one doesn't get assigned:
        vocabulary.refresh_from_db()

        recipient_region_attributes = {
            "code": region.code,
            "vocabulary": str(vocabulary.code),
            "percentage": '100',
            "vocabulary-uri": "http://www.google.lt",
        }

        recipient_region_XML_element = E(
            'recipient-region',
            **recipient_region_attributes
        )

        self.parser_203.iati_activities__iati_activity__recipient_region(
            recipient_region_XML_element)

        recipient_region = self.parser_203.get_model(
            'ActivityRecipientRegion')

        self.assertEqual(
            recipient_region.region, region
        )

        self.assertEqual(
            recipient_region.activity, self.activity
        )

        self.assertEqual(
            recipient_region.percentage,
            Decimal(recipient_region_attributes['percentage'])
        )

        self.assertEqual(
            recipient_region.vocabulary_uri,
            recipient_region_attributes['vocabulary-uri']
        )

        self.assertEqual(recipient_region.vocabulary, vocabulary)

        # Saving models is not tested here:
        self.assertEqual(recipient_region.pk, None)


class ActivitySectorTestCase(TestCase):
    """
    2.03: 'percentage' attribute must be a decimal number between 0 and 100
    inclusive, WITH NO PERCENTAGE SIGN
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

        assert (isinstance(self.parser_203, Parser_203))

        # Version
        current_version = VersionFactory(code='2.03')

        # Related objects:
        self.activity = iati_factory.ActivityFactory.create(
            iati_standard_version=current_version
        )

        self.parser_203.register_model('Activity', self.activity)

    def test_activity_sector(self):
        """
        - Tests if '<sector>' xml element is parsed and saved
          correctly with proper attributes and narratives
        - Doesn't test if object is actually saved in the database (the final
          stage), because 'save_all_models()' parser's function is (probably)
          tested separately
        """

        sector_attributes = {
            # "code": '1',
        }

        sector_XML_element = E(
            'sector',
            **sector_attributes
        )

        # CASE 1:
        # 'Code' attr is missing:
        try:
            self.parser_203.iati_activities__iati_activity__sector(
                sector_XML_element)
            self.assertFail()
        except RequiredFieldError as inst:
            self.assertEqual(inst.model, 'sector')
            self.assertEqual(inst.field, 'code')
            self.assertEqual(inst.message, 'required attribute missing')

        # CASE 2:
        # Vocabulary not found:

        sector_attributes = {
            "code": '1',
            "vocabulary": '222',
        }

        sector_XML_element = E(
            'sector',
            **sector_attributes
        )

        try:
            self.parser_203.iati_activities__iati_activity__sector(
                sector_XML_element)
            self.assertFail()
        except FieldValidationError as inst:
            self.assertEqual(inst.model, 'sector')
            self.assertEqual(inst.field, 'vocabulary')
            self.assertEqual(
                inst.message,
                "not found on the accompanying code list"
            )

        # CASE 3:
        # Region not found (when code attr == 1):

        # Create Vocabulary obj:
        vocabulary = SectorVocabularyFactory(code=1)

        # Clear codelist cache (from memory):
        self.parser_203.codelist_cache = {}

        # Clear codelist cache (from memory):
        self.parser_203.codelist_cache = {}

        sector_attributes = {
            "code": '1',
            "vocabulary": str(vocabulary.code),
        }

        sector_XML_element = E(
            'sector',
            **sector_attributes
        )

        try:
            self.parser_203.iati_activities__iati_activity__sector(
                sector_XML_element)
            self.assertFail()
        except FieldValidationError as inst:
            self.assertEqual(inst.model, 'sector')
            self.assertEqual(inst.field, 'code')
            self.assertEqual(
                inst.message,
                "not found on the accompanying code list"
            )

        # CASE 4:
        # Sector not found (when code attr is differnt):

        # Update Vocabulary obj:
        vocabulary.code = 222
        vocabulary.save()

        # Clear codelist cache (from memory):
        self.parser_203.codelist_cache = {}

        sector_attributes = {
            "code": '1',
            "vocabulary": str(vocabulary.code),
        }

        sector_XML_element = E(
            'sector',
            **sector_attributes
        )

        try:
            self.parser_203.iati_activities__iati_activity__sector(
                sector_XML_element)
            self.assertFail()
        except IgnoredVocabularyError as inst:
            self.assertEqual(inst.model, 'sector')
            self.assertEqual(inst.field, 'vocabulary')
            self.assertEqual(
                inst.message, 'non implemented vocabulary'
            )

        # CASE 5:
        # percentage is wrong:

        # Update Vocabulary obj:
        vocabulary.code = 1
        vocabulary.save()

        sector = iati_factory.SectorFactory()

        # Clear codelist cache (from memory):
        self.parser_203.codelist_cache = {}

        sector_attributes = {
            "code": sector.code,
            "vocabulary": str(vocabulary.code),
            "percentage": '100%'
        }

        sector_XML_element = E(
            'sector',
            **sector_attributes
        )

        try:
            self.parser_203.iati_activities__iati_activity__sector(
                sector_XML_element)
            self.assertFail()
        except FieldValidationError as inst:
            self.assertEqual(inst.model, 'sector')
            self.assertEqual(inst.field, 'percentage')
            self.assertEqual(
                inst.message,
                'percentage value is not valid'
            )

        # CASE 6:
        # All is good:

        # Refresh related object so old one doesn't get assigned:
        sector.refresh_from_db()
        vocabulary.refresh_from_db()

        sector_attributes = {
            "code": sector.code,
            "vocabulary": str(vocabulary.code),
            "percentage": '100',
            "vocabulary-uri": "http://www.google.lt",
        }

        sector_XML_element = E(
            'sector',
            **sector_attributes
        )

        self.parser_203.iati_activities__iati_activity__sector(
            sector_XML_element)

        activity_sector = self.parser_203.get_model(
            'ActivitySector')

        self.assertEqual(
            activity_sector.sector, sector
        )

        self.assertEqual(
            activity_sector.activity, self.activity
        )

        self.assertEqual(
            activity_sector.percentage,
            Decimal(sector_attributes['percentage'])
        )

        self.assertEqual(
            activity_sector.vocabulary_uri,
            sector_attributes['vocabulary-uri']
        )

        self.assertEqual(activity_sector.vocabulary, vocabulary)

        # Saving models is not tested here:
        self.assertEqual(activity_sector.pk, None)


class AidTypeTestCase(TestCase):
    """
    2.03: Added new @vocabulary attributes for elements relating to aid-type
    """

    def setUp(self):

        AidTypeVocabularyFactory(name='OECD DAC')

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

        assert (isinstance(self.parser_203, Parser_203))

        # Version
        current_version = VersionFactory(code='2.03')

        # Related objects:
        self.activity = iati_factory.ActivityFactory.create(
            iati_standard_version=current_version,
            default_aid_type=None,
        )

        self.transaction = TransactionFactory(
            activity=self.activity
        )

        self.parser_203.register_model('Transaction', self.transaction)
        self.parser_203.register_model('Activity', self.activity)

    # TODO: update test with multiple TransactionAidTypes:
    def test_transaction_aid_type(self):
        """
        - Tests if '<aid-type>' xml element is parsed and saved
          correctly with proper attributes and narratives
        - Doesn't test if object is actually saved in the database (the final
          stage), because 'save_all_models()' parser's function is (probably)
          tested separately
        """

        aid_type_attributes = {
            # "code": '1',
        }

        aid_type_XML_element = E(
            'aid-type',
            **aid_type_attributes
        )

        # CASE 1:
        # 'Code' attr is missing:
        try:
            self.parser_203.\
                iati_activities__iati_activity__transaction__aid_type(
                # NOQA: E501
                aid_type_XML_element)
            self.assertFail()
        except RequiredFieldError as inst:
            self.assertEqual(inst.model, 'iati-activity/transaction/aid-type')
            self.assertEqual(inst.field, 'code')
            self.assertEqual(inst.message, 'required attribute missing')

        # CASE 2:
        # 'AidType' codelist not found:
        aid_type_attributes = {
            "code": '1',
        }

        aid_type_XML_element = E(
            'aid-type',
            **aid_type_attributes
        )

        try:
            self.parser_203.\
                iati_activities__iati_activity__transaction__aid_type(
                # NOQA: E501
                aid_type_XML_element)
            self.assertFail()
        except FieldValidationError as inst:
            self.assertEqual(inst.model, 'transaction/aid-type')
            self.assertEqual(inst.field, 'code')
            self.assertEqual(
                inst.message,
                "not found on the accompanying code list. Note, that custom "
                "AidType Vocabularies currently are not supported"
            )

        # CASE 3: All is good
        # let's create an AidTypeVocabulary and AidType elements (so the
        # parser doesn't complain):
        aid_type_vocabulary = AidTypeVocabularyFactory(code='3')
        aid_type = codelist_factory.AidTypeFactory(
            code='3',
            vocabulary=aid_type_vocabulary
        )

        # Clear codelist cache (from memory):
        self.parser_203.codelist_cache = {}

        aid_type_attributes = {
            "code": aid_type.code,
            'vocabulary': aid_type_vocabulary.code,
        }

        aid_type_XML_element = E(
            'aid-type',
            **aid_type_attributes
        )

        self.parser_203.iati_activities__iati_activity__transaction__aid_type(
            # NOQA: E501
            aid_type_XML_element)

        transaction = self.parser_203.get_model('Transaction')

        transaction_aid_type = self.parser_203.get_model('TransactionAidType')

        self.assertEqual(
            transaction_aid_type.transaction, transaction
        )
        self.assertEqual(
            transaction_aid_type.aid_type, aid_type
        )


class ActivityResultDocumentLinkTestCase(TestCase):

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

        assert (isinstance(self.parser_203, Parser_203))

        # Version
        current_version = VersionFactory(code='2.03')

        # Related objects:
        self.activity = iati_factory.ActivityFactory.create(
            iati_standard_version=current_version
        )
        self.result = iati_factory.ResultFactory.create()

        self.parser_203.register_model('Activity', self.activity)
        self.parser_203.register_model('Result', self.result)

    def test_activity_result_document_link(self):

        # Case 1:
        #  'url is missing'

        result_document_link_attr = {
            # url = 'missing'

            "format": 'something'

            # 'format_code' will be got in the function

        }
        result_document_link_XML_element = E(
            'document_link',
            **result_document_link_attr
        )

        try:
            self.parser_203.\
                iati_activities__iati_activity__result__document_link(
                    result_document_link_XML_element)
            self.assertFail()
        except RequiredFieldError as inst:
            self.assertEqual(inst.field, 'url')
            self.assertEqual(inst.message, 'required attribute missing')

        # Case 2:
        # 'file_format' is missing

        result_document_link_attr = {
            "url": 'www.google.com'

            # "format":
            # 'format_code' will be got in the function

        }
        result_document_link_XML_element = E(
            'document-link',
            **result_document_link_attr
        )
        try:
            self.parser_203.\
                iati_activities__iati_activity__result__document_link(
                    result_document_link_XML_element
                )
            self.assertFail()
        except RequiredFieldError as inst:
            self.assertEqual(inst.field, 'format')
            self.assertEqual(inst.message, 'required attribute missing')

        # Case 3;
        # 'file_format_code' is missing

        result_document_link_attr = {
            "url": 'www.google.com',
            "format": 'something',
            # 'format_code will be got in the function

        }
        result_document_link_XML_element = E(
            'document-link',
            **result_document_link_attr
        )
        try:
            self.parser_203.\
                iati_activities__iati_activity__result__document_link(
                    result_document_link_XML_element
                )
            self.assertFail()
        except FieldValidationError as inst:
            self.assertEqual(inst.field, 'format')
            self.assertEqual(inst.message, 'not found on the accompanying '
                                           'code list')

        # Case 4;
        # all is good

        # dummy document-link object
        dummy_file_format = codelist_factory.\
            FileFormatFactory(code='application/pdf')

        dummy_document_link = iati_factory.\
            DocumentLinkFactory(url='http://aasamannepal.org.np/')

        self.parser_203.codelist_cache = {}

        result_document_link_attr = {
            "url": dummy_document_link.url,
            "format": dummy_file_format.code

        }
        result_document_link_XML_element = E(
            'document-link',
            **result_document_link_attr
        )

        self.parser_203 \
            .iati_activities__iati_activity__result__document_link(
                result_document_link_XML_element
            )

        document_link = self.parser_203.get_model('DocumentLink')

        # checking if everything is saved

        self.assertEqual(document_link.url, dummy_document_link.url)
        self.assertEqual(document_link.file_format,
                         dummy_document_link.file_format)
        self.assertEqual(document_link.activity, self.activity)
        self.assertEqual(document_link.result, self.result)


class ResultDocumentLinkTitleTestCase(TestCase):

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

        assert (isinstance(self.parser_203, Parser_203))

        # Version
        current_version = VersionFactory(code='2.03')

        # Related objects:
        self.activity = iati_factory.ActivityFactory.create(
            iati_standard_version=current_version
        )
        self.document_link = iati_factory.DocumentLinkFactory. \
            create(url='http://someuri.com')

        self.parser_203.register_model('Activity', self.activity)
        self.parser_203.register_model('DocumentLink', self.document_link)

    def test_result_document_link_title(self):

        dummy_file_format = codelist_factory. \
            FileFormatFactory(code='application/pdf')

        dummy_document_link = iati_factory. \
            DocumentLinkFactory(url='http://aasamannepal.org.np/')

        self.parser_203.codelist_cache = {}

        result_document_link_attr = {
            "url": dummy_document_link.url,
            "format": dummy_file_format.code

        }
        result_document_link_XML_element = E(
            'document-link',
            **result_document_link_attr
        )
        self.parser_203 \
            .iati_activities__iati_activity__result__document_link__title(
                result_document_link_XML_element)
        document_link_title = self.parser_203.get_model(
            'DocumentLinkTitle')

        self.assertEqual(self.document_link,
                         document_link_title.document_link)


class ResultDocumentLinkTitleTestCase(TestCase):

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

        assert (isinstance(self.parser_203, Parser_203))

        # Version
        current_version = VersionFactory(code='2.03')

        # Related objects:
        self.activity = iati_factory.ActivityFactory.create(
            iati_standard_version=current_version
        )
        self.document_link = iati_factory.DocumentLinkFactory. \
            create(url='http://someuri.com')

        self.parser_203.register_model('Activity', self.activity)
        self.parser_203.register_model('DocumentLink', self.document_link)

    def test_result_document_link_title(self):

        dummy_file_format = codelist_factory. \
            FileFormatFactory(code='application/pdf')

        dummy_document_link = iati_factory. \
            DocumentLinkFactory(url='http://aasamannepal.org.np/')

        self.parser_203.codelist_cache = {}

        result_document_link_attr = {
            "url": dummy_document_link.url,
            "format": dummy_file_format.code

        }
        result_document_link_XML_element = E(
            'document-link',
            **result_document_link_attr
        )
        self.parser_203 \
            .iati_activities__iati_activity__result__document_link__title(
                result_document_link_XML_element)
        document_link_title = self.parser_203.get_model(
            'DocumentLinkTitle')

        self.assertEqual(self.document_link,
                         document_link_title.document_link)

class ResultDocumentLinkDocumentDateTestCase(TestCase):

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

        assert (isinstance(self.parser_203, Parser_203))

        # Version
        current_version = VersionFactory(code='2.03')

        # Related objects:
        self.activity = iati_factory.ActivityFactory.create(
            iati_standard_version=current_version
        )
        self.document_link = iati_factory.DocumentLinkFactory. \
            create(url='http://someuri.com')

        self.parser_203.register_model('Activity', self.activity)
        self.parser_203.register_model('DocumentLink', self.document_link)

    def test_result_document_link_document_date(selfs):
        result_document_link_attr = {
            "url": 'www.google.com',
            "format": 'something',
            # 'format_code will be got in the function

        }
        result_document_link_XML_element = E(
            'document-link',
            **result_document_link_attr
        )
        selfs.parser_203\
            .iati_activities__iati_activity__result__document_link__document_date(
            result_document_link_XML_element
        )


class ActivityResultIndicatorDocumentLinkTestCase(TestCase):

    """
    2.03: The optional document-link element was added.
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

        assert (isinstance(self.parser_203, Parser_203))

        # Related objects:
        self.result_indicator = iati_factory.ResultIndicatorFactory.create()
        self.activity = self.result_indicator.result.activity
        self.result = self.result_indicator.result

        self.parser_203.register_model('Activity', self.activity)
        self.parser_203.register_model('Result', self.result)
        self.parser_203.register_model(
            'ResultIndicator', self.result_indicator
        )

    def test_activity_result_indicator_document_link(self):

        # Case 1:
        #  'url is missing'

        result_indicator_document_link_attr = {
            # url = 'missing'

            "format": 'something'

            # 'format_code' will be got in the function

        }
        result_indicator_document_link_XML_element = E(
            'document_link',
            **result_indicator_document_link_attr
        )

        try:
            self.parser_203.\
                iati_activities__iati_activity__result__indicator__document_link(  # NOQA: E501
                    result_indicator_document_link_XML_element)
            self.assertFail()
        except RequiredFieldError as inst:
            self.assertEqual(inst.field, 'url')
            self.assertEqual(inst.message, 'required attribute missing')

        # Case 2:
        # 'file_format' is missing

        result_indicator_document_link_attr = {
            "url": 'www.google.com'

            # "format":
            # 'format_code' will be got in the function

        }
        result_indicator_document_link_XML_element = E(
            'document-link',
            **result_indicator_document_link_attr
        )
        try:
            self.parser_203.\
                iati_activities__iati_activity__result__indicator__document_link(  # NOQA: E501
                    result_indicator_document_link_XML_element
                )
            self.assertFail()
        except RequiredFieldError as inst:
            self.assertEqual(inst.field, 'format')
            self.assertEqual(inst.message, 'required attribute missing')

        # Case 3;
        # 'file_format_code' is missing

        result_indicator_document_link_attr = {
            "url": 'www.google.com',
            "format": 'something',
            # 'format_code will be got in the function

        }
        result_indicator_document_link_XML_element = E(
            'document-link',
            **result_indicator_document_link_attr
        )
        try:
            self.parser_203.\
                iati_activities__iati_activity__result__indicator__document_link(  # NOQA: E501
                    result_indicator_document_link_XML_element
                )
            self.assertFail()
        except FieldValidationError as inst:
            self.assertEqual(inst.field, 'format')
            self.assertEqual(inst.message, 'not found on the accompanying '
                                           'code list')

        # Case 4;
        # all is good

        # dummy document-link object
        dummy_file_format = codelist_factory.\
            FileFormatFactory(code='application/pdf')

        dummy_document_link = iati_factory.\
            DocumentLinkFactory(url='http://aasamannepal.org.np/')

        self.parser_203.codelist_cache = {}

        result_indicator_document_link_attr = {
            "url": dummy_document_link.url,
            "format": dummy_file_format.code

        }
        result_indicator_document_link_XML_element = E(
            'document-link',
            **result_indicator_document_link_attr
        )

        self.parser_203 \
            .iati_activities__iati_activity__result__indicator__document_link(
                result_indicator_document_link_XML_element
            )

        result_indicator_document_link = self.parser_203.get_model(
            'DocumentLink'
        )

        # checking if everything is saved

        self.assertEqual(
            result_indicator_document_link.url,
            dummy_document_link.url
        )
        self.assertEqual(
            result_indicator_document_link.file_format,
            dummy_document_link.file_format
        )
        self.assertEqual(
            result_indicator_document_link.activity,
            self.activity
        )
        self.assertEqual(
            result_indicator_document_link.result_indicator,
            self.result_indicator
        )


class ActivityResultIndicatorDocumentLinkDocumentDateTestCase(TestCase):

    """
    2.03: The optional document-date element of a document-link in a indicator
    in a result element was added.
    """

    def setUp(self):
        # 'Main' XML file for instantiating parser:
        xml_file_attrs = {
            "generated-datetime": datetime.datetime.now().isoformat(),
            "version": '2.03',
        }
        self.iati_203_XML_file = E("iati-activities", **xml_file_attrs)

        dummy_source = synchroniser_factory.DatasetFactory.create()

        self.parser_203 = ParseManager(
            dataset=dummy_source,
            root=self.iati_203_XML_file,
        ).get_parser()

        self.parser_203.default_lang = "en"

        assert (isinstance(self.parser_203, Parser_203))

        # Related objects:
        self.document_link = iati_factory.DocumentLinkFactory.create()
        self.result_indicator = self.document_link.result_indicator
        self.activity = self.result_indicator.result.activity
        self.result = self.result_indicator.result

        self.parser_203.register_model('Activity', self.activity)
        self.parser_203.register_model('Result', self.result)
        self.parser_203.register_model(
            'ResultIndicator', self.result_indicator
        )
        self.parser_203.register_model(
            'DocumentLink', self.document_link
        )

    def test_activity_result_indicator_document_link_document_date(self):

        # Case 1: 'ido-date' attribute is missing:

        document_date_attr = {
            # 'iso-date': '2018-10-10',
        }

        document_date_XML_element = E(
            'document-date',
            **document_date_attr
        )

        try:
            self.parser_203.\
                iati_activities__iati_activity__result__indicator__document_link__document_date(  # NOQA: E501
                    document_date_XML_element)
            self.assertFail()
        except RequiredFieldError as inst:
            self.assertEqual(inst.field, 'iso-date')
            self.assertEqual(inst.message, 'required attribute missing')

        # Case 2:
        # ISO date is invalid:

        document_date_attr = {
            'iso-date': '2018-10-ab',
        }
        document_date_XML_element = E(
            'document-date',
            **document_date_attr
        )

        try:
            self.parser_203.\
                iati_activities__iati_activity__result__indicator__document_link__document_date(  # NOQA: E501
                    document_date_XML_element)
            self.assertFail()
        except RequiredFieldError as inst:
            self.assertEqual(inst.field, 'iso-date')
            self.assertEqual(inst.message, 'Unspecified or invalid. Date should be of type xml:date.')

        # Case 3:
        # all is good:

        document_date_attr = {
            'iso-date': '2018-10-10',
        }
        document_date_XML_element = E(
            'document-date',
            **document_date_attr
        )

        self.parser_203.\
            iati_activities__iati_activity__result__indicator__document_link__document_date(  # NOQA: E501
                document_date_XML_element
            )

        result_indicator_document_link = self.parser_203.get_model(
            'DocumentLink'
        )

        self.assertEqual(
            result_indicator_document_link.iso_date,
            datetime.datetime(2018, 10, 10, 0, 0)
        )
