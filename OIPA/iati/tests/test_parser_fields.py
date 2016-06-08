"""
    Unit tests for all fields in the parser, for multiple IATI versions.
"""

import copy
import datetime

from decimal import Decimal
from decimal import InvalidOperation
from lxml import etree
from lxml.builder import E

from django.core import management
from django.test import TestCase # Runs each test in a transaction and flushes database
from unittest import skip
from mock import MagicMock

from iati.factory import iati_factory
from iati.transaction import factories as transaction_factory
from iati.parser.parse_manager import ParseManager

from iati_synchroniser.models import IatiXmlSource
import iati.models as iati_models
import iati_codelists.models as codelist_models

from currency_convert import convert
from iati.parser.post_save import *

from iati.parser.IATI_1_03 import Parse as Parser_103
from iati.parser.IATI_1_05 import Parse as Parser_105
from iati.parser.IATI_2_01 import Parse as Parser_201
from iati.parser.exceptions import ValidationError

# TODO: replace fixtures with factoryboy classes - 2015-12-02
# TODO: Setup parser classes per test, to isolate tests as much as possible (currently per class) - 2015-12-02
# TODO: Refactor this file into multiple files - 2015-12-02


def build_xml(version, iati_identifier):
    """
        Construct a base activity file to work with in the tests
    """

    activities_attrs = { "generated-datetime": datetime.datetime.now().isoformat(),
        "version": version,
        "linked-data-default": "http://zimmermanzimmerman.org/",
    }

    activity = E("iati-activities", 
        **activities_attrs
    )
    
    return activity

# def create_dummy_source(url, title, name, current_publisher, cur_type):
#     source = IatiXmlSource(
#         ref=name,
#         title=title,
#         publisher=current_publisher,
#         source_url=url,
#         type=cur_type)

#     source.save(process=False, added_manually=False)
#     return source


def copy_xml_tree(tree):
    return copy.deepcopy(tree)


def build_activity(version="2.01", *args, **kwargs):
        activity = iati_factory.ActivityFactory.build(
            iati_standard_version=codelist_models.Version.objects.get(code=version), # TODO: cache this
            *args,
            **kwargs
        )
        return activity


def create_parser(self, version="2.01"):
    iati_identifier = "NL-KVK-51018586-0666"

    iati_activities = build_xml(version, iati_identifier)
    dummy_source = IatiXmlSource.objects.get(id=1)

    return ParseManager(dummy_source, iati_activities).get_parser()


def create_parsers(versions=["2.01", "1.05"]):
    return {version: create_parser(version) for version in versions}


def setUpModule():
    fixtures = ['test_publisher.json', 'test_vocabulary', 'test_codelists.json', 'test_geodata.json']

    for fixture in fixtures:
        management.call_command("loaddata", fixture)


def tearDownModule():
    management.call_command('flush', interactive=False, verbosity=0)


class ParserSetupTestCase(TestCase):

    # fixtures = ['test_publisher.json', 'test_codelists.json', 'test_vocabulary', 'test_geodata.json']

    def _get_activity(self, iati_identifier):
        return iati_models.Activity.objects.get(id=iati_identifier)

    @classmethod
    def setUpClass(self):
        # for fixture in self.fixtures:
        #     management.call_command("loaddata", fixture) 
        self.iati_identifier = "NL-KVK-51018586-0666"
        self.alt_iati_identifier = "NL-KVK-51018586-0667"

        self.iati_103 = build_xml("1.03", self.iati_identifier)
        self.iati_104 = build_xml("1.04", self.iati_identifier)
        self.iati_105 = build_xml("1.05", self.iati_identifier)
        self.iati_201 = build_xml("2.01", self.iati_identifier)

        # publisher = Publisher.objects.get(id=1) # from fixture
        # dummy_source = create_dummy_source("http://zimmermanzimmerman.org/iati", "ZnZ", "Zimmerman", publisher, 1)
        dummy_source = IatiXmlSource.objects.get(id=1)

        self.parser_103 = ParseManager(dummy_source, self.iati_103).get_parser()
        self.parser_104 = ParseManager(dummy_source, self.iati_104).get_parser()
        self.parser_105 = ParseManager(dummy_source, self.iati_105).get_parser()
        self.parser_201 = ParseManager(dummy_source, self.iati_201).get_parser()

        self.parser_103.default_lang = "en"
        self.parser_104.default_lang = "en"
        self.parser_105.default_lang = "en"
        self.parser_201.default_lang = "en"

        assert(isinstance(self.parser_103, Parser_103))
        assert(isinstance(self.parser_104, Parser_105))
        assert(isinstance(self.parser_105, Parser_105))
        assert(isinstance(self.parser_201, Parser_201))

        # todo: self.assertTrue source was handled appropriately
        # self.self.assertTrueEqual(self.parser_103.iati_source, self.parser_104.iati_source, self.parser_105.iati_source, self.parser_201.iati_source)

    @classmethod
    def tearDownClass(self):
        pass


class GenericMethodsTestCase(ParserSetupTestCase):
    """
    test of helper methods available in the parser
    """
    def setUp(self):
        self.iati_201 = copy_xml_tree(self.iati_201)

        self.title = E('title', )
        self.narrative = E('narrative', "random text")

        self.activity = build_activity(version="2.01")
        self.parser_201.register_model('Activity', self.activity)
        self.parser_105.register_model('Activity', self.activity)


class ActivityTestCase(ParserSetupTestCase):
    """
    iati_activities__iati_activity
    CHANGELOG
    2.01: The version attribute was removed.
    1.02: Introduced the linked-data-uri attribute on iati-activity element
    """
    def setUp(self):
        self.iati_201 = copy_xml_tree(self.iati_201)

        # sample attributes on iati-activity xml
        self.attrs = {
            # "xml:lang": "en",
            "default-currency": "USD",
            "last-updated-datetime": datetime.datetime.now().isoformat(' '),
            "linked-data-uri": "http://zimmermanzimmerman.org/iati",
            "hierarchy": "1"
        }

        # default activity model fields
        self.defaults = {
            "hierarchy": 1,
        }

        iati_activity = E("iati-activity", **self.attrs)
        iati_activity.append(E("iati-identifier", self.iati_identifier))
        self.iati_201.append(iati_activity) 
        self.iati_201.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en" # ISO 639-1:2002
        # print(etree.tostring(self.iati_201, pretty_print=True))

        activity = build_activity(version="2.01")
        # self.parser_201.register_model('Activity', activity)
        # self.parser_201.register_model('Activity', activity)

    @skip('NotImplemented')
    def test_add_narrative(self):
        """
        Check if the narrative element is parsed correctly 
        """

    def test_activity_201(self):
        """
        Check complete element is parsed correctly
        """
        self.parser_201.iati_activities__iati_activity(self.iati_201.find('iati-activity'))

        activity = self.parser_201.get_model('Activity')
        # self.parser_201.save_model('Activity')

        self.assertTrue(activity.default_currency.code == self.attrs["default-currency"])
        self.assertTrue(str(activity.last_updated_datetime) == self.attrs["last-updated-datetime"])
        self.assertTrue(activity.linked_data_uri == self.attrs["linked-data-uri"])
        self.assertTrue(activity.hierarchy == self.attrs["hierarchy"])
        self.assertTrue(activity.iati_standard_version.code == "2.01")

    def test_activity_default_201(self):
        """
        Check defaults are set accordingly
        """
        iati_201 = copy_xml_tree(self.iati_201)

        iati_activity = iati_201.find('iati-activity') 
        del iati_activity.attrib[ 'default-currency' ]
        del iati_activity.attrib[ 'last-updated-datetime' ]
        # del iati_activity.attrib[ 'xml:lang' ]
        del iati_activity.attrib[ 'hierarchy' ]
        del iati_activity.attrib[ 'linked-data-uri' ]

        self.parser_201.iati_activities__iati_activity(iati_activity)
        activity = self.parser_201.get_model('Activity')

        for field, default in self.defaults.iteritems():
            self.assertTrue(getattr(activity, field) == default)
        self.assertTrue(activity.iati_standard_version.code == "2.01")


    def check_parsed(self, old_activity, new_activity, overwrites=True):
        """
        helper method for 4 tests below, which determine whether the activity should be parsed or not
        """
        self.parser_201.iati_activities__iati_activity(old_activity)
        self.parser_201.get_model('Activity').save()

        if overwrites: 
            self.parser_201.iati_activities__iati_activity(new_activity)
            self.parser_201.get_model('Activity').save()
        else:
            with self.assertRaises(Exception):
                self.parser_201.iati_activities__iati_activity(new_activity)
                self.parser_201.get_model('Activity').save()

        # activity = self.parser_201.get_model('Activity')

        # if overwrites:
        #     self.assertTrue(activity.id == new_activity.xpath('iati-identifier/text()')[0])
        # else:
        #     print(activity.id)
        #     print(old_activity.xpath('iati-identifier/text()')[0])
        #     self.assertTrue(activity.id == old_activity.xpath('iati-identifier/text()')[0] )

    def test_activity_greater_last_updated_time_should_parse(self):
        """
        case 1: new activity.last-updated-datetime >= old activity.last-updated-datetime => parse new activity
        """
        old_activity = copy_xml_tree(self.iati_201).find('iati-activity')
        new_activity = copy_xml_tree(self.iati_201).find('iati-activity')

        # case 1 (greater)
        old_activity.attrib["last-updated-datetime"] = (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat() 
        new_activity.attrib["last-updated-datetime"] = datetime.datetime.now().isoformat()
        self.check_parsed(old_activity, new_activity, True)

        # case 1 (equivalence) => do not re-parse, keep current activity
        time = datetime.datetime.now().isoformat()
        old_activity.attrib["last-updated-datetime"] = time
        new_activity.attrib["last-updated-datetime"] = time
        self.check_parsed(old_activity, new_activity, False)

    def test_activity_smaller_last_updated_time_should_not_parse(self):
        """
        case 2: new activity.last-updated-datetime < old activity.last-updated-datetime => Don't parse new activity
        """
        old_activity = copy_xml_tree(self.iati_201).find('iati-activity')
        new_activity = copy_xml_tree(self.iati_201).find('iati-activity')

        # case 2
        old_activity.attrib["last-updated-datetime"] = datetime.datetime.now().isoformat()
        new_activity.attrib["last-updated-datetime"] = (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat() 
        self.check_parsed(old_activity, new_activity, False)

    def test_activity_last_updated_time_absent_old_activity_present_should_not_parse(self):
        """
        case 3: new activity.last-updated-datetime is absent and old activity.last-updated-datetime is present => Don't parse
        """
        old_activity = copy_xml_tree(self.iati_201).find('iati-activity')
        new_activity = copy_xml_tree(self.iati_201).find('iati-activity')

        # case 3
        old_activity.attrib["last-updated-datetime"] = datetime.datetime.now().isoformat()
        del new_activity.attrib["last-updated-datetime"]
        self.check_parsed(old_activity, new_activity, False)

    def test_activity_last_updated_time_absent_old_activity_absent_should_parse(self):
        """
        case 4: new activity.last-updated-datetime is absent and old activity.last-updated-datetime is absent => Parse
        """
        old_activity = copy_xml_tree(self.iati_201).find('iati-activity')
        new_activity = copy_xml_tree(self.iati_201).find('iati-activity')

        # case 4
        del old_activity.attrib["last-updated-datetime"]
        del new_activity.attrib["last-updated-datetime"]
        self.check_parsed(old_activity, new_activity, True)

    @skip('NotImplemented')
    def test_activity_linked_data_uri_inherited(self):
        """
        Check linked-data-uri is inherited from iati-activities if set
        """
        raise NotImplementedError()

        linked_data_default ="http://zimmermanzimmerman.org/"

        iati_201 = copy_xml_tree(self.iati_201)
        iati_201.set("linked-data-default", linked_data_default)

        iati_activity = iati_201.find('iati-activity')
        del iati_activity.attrib['linked-data-uri']

        self.parser_201.iati_activities__iati_activity(iati_activity)
        activity = self.parser_201.get_model('Activity')

        self.assertTrue(activity.linked_data_uri == linked_data_default)

    def test_iati_identifier(self):
        """
        iati_activities__iati_activity__iati_identifier
        should raise exception if not present
        """
        iati_201 = copy_xml_tree(self.iati_201)
        iati_identifier = iati_201.find('iati-activity').find('iati-identifier')

        self.parser_201.iati_activities__iati_activity__iati_identifier(iati_identifier)
        activity = self.parser_201.get_model('Activity')

        self.assertTrue(activity.iati_identifier == iati_identifier.text)

        # empty iati-idenifier should throw exception
        iati_identifier.text = ""

        with self.assertRaises(Exception):
            self.parser_201.iati_activities__iati_activity__iati_identifier(iati_identifier)


    def test_capital_spend(self):
        """
        iati_activities__capital_spend
        CHANGELOG
        1.03: This is a new element, introduced in version 1.03 of the standard
        """
        percentage = "80.91"

        iati_activity = copy_xml_tree(self.iati_201).find("iati-activity")
        iati_activity.append(E('capital-spend', percentage=percentage))
        capital_spend = iati_activity.find('capital-spend')

        activity = iati_factory.ActivityFactory.build(
            iati_standard_version=codelist_models.Version.objects.get(code="2.01")
        )

        self.parser_201.register_model('Activity', activity)
        self.parser_201.iati_activities__iati_activity__capital_spend(capital_spend)
        activity = self.parser_201.get_model('Activity')

        self.assertTrue(activity.capital_spend == percentage)

    @skip('NotImplemented')
    def test_has_conditions_returns_true(self):
        raise NotImplementedError()
        # attached = '1'

        # iati_activity = copy_xml_tree(self.iati_201).find("iati-activity")
        # iati_activity.append(E('conditions', attached=attached))
        # conditions = iati_activity.find('conditions')
        
        # activity = build_activity(version="2.01")

        # self.parser_201.register_model('Activity', activity)
        # self.parser_201.iati_activities__iati_activity__conditions(conditions)
        # activity = self.parser_201.get_model('Activity')
        # activity.save()

        # self.assertTrue(activity.has_conditions == True)

    @skip('NotImplemented')
    def test_has_conditions_returns_false(self):
        raise NotImplementedError()
        # attached = '0'

        # iati_activity = copy_xml_tree(self.iati_201).find("iati-activity")
        # iati_activity.append(E('conditions', attached=attached))
        # conditions = iati_activity.find('conditions')
        
        # activity = build_activity(version="2.01")

        # self.parser_201.register_model('Activity', activity)
        # self.parser_201.iati_activities__iati_activity__conditions(conditions)
        # activity = self.parser_201.get_model('Activity')
        # activity.save()

        # self.assertTrue(activity.has_conditions == False)

    def test_activity_status(self):
        code = '1' # Pipeline/identification

        activity_status = E('activity-status', code=code)
        self.parser_201.iati_activities__iati_activity__activity_status(activity_status)

        activity = self.parser_201.get_model('Activity')
        self.assertTrue(activity.activity_status.code == code)

    def test_activity_scope(self):
        """
        2.01: Freetext is no longer allowed within this element.
        1.03: This is a new element, introduced in version 1.03 of the standard
        """
        code = '1' # Global

        activity_scope = E('activity-scope', code=code)
        self.parser_201.iati_activities__iati_activity__activity_scope(activity_scope)

        activity = self.parser_201.get_model('Activity')
        self.assertTrue(activity.scope.code == code)

    def test_collaboration_type(self):
        """
        2.01: Freetext is no longer allowed within this element.
        """
        code = '1' # Global

        collaboration_type = E('collaboration-type', code=code)
        self.parser_201.iati_activities__iati_activity__collaboration_type(collaboration_type)

        activity = self.parser_201.get_model('Activity')
        self.assertTrue(activity.collaboration_type.code == code)

    def test_default_flow_type(self):
        """
        2.01: Freetext is no longer allowed within this element.
        """
        code = '10' # ODA

        default_flow_type = E('default-flow-type', code=code)
        self.parser_201.iati_activities__iati_activity__default_flow_type(default_flow_type)

        activity = self.parser_201.get_model('Activity')
        self.assertTrue(activity.default_flow_type.code == code)

    def test_default_finance_type(self):
        """
        2.01: Freetext is no longer allowed within this element.
        """
        code = '310' # Deposit basis

        default_finance_type = E('default-finance-type', code=code)
        self.parser_201.iati_activities__iati_activity__default_finance_type(default_finance_type)

        activity = self.parser_201.get_model('Activity')
        self.assertTrue(activity.default_finance_type.code == code)

    def test_default_aid_type(self):
        """
        2.01: Freetext is no longer allowed within this element.
        """
        code = 'A01' # General Budget Support

        default_aid_type = E('default-aid-type', code=code)
        self.parser_201.iati_activities__iati_activity__default_aid_type(default_aid_type)

        activity = self.parser_201.get_model('Activity')
        self.assertTrue(activity.default_aid_type.code == code)

    def test_default_tied_status(self):
        """
        2.01: Freetext is no longer allowed within this element.
        """
        code = '4' # Tied

        default_tied_status = E('default-tied-status', code=code)
        self.parser_201.iati_activities__iati_activity__default_tied_status(default_tied_status)

        activity = self.parser_201.get_model('Activity')
        self.assertTrue(activity.default_tied_status.code == code)

class TitleTestCase(ParserSetupTestCase):
    def setUp(self):
        self.iati_201 = copy_xml_tree(self.iati_201)

        self.title = E('title', )
        self.narrative = E('narrative', "random text")

        self.activity = build_activity(version="2.01")
        self.parser_201.register_model('Activity', self.activity)
        self.parser_105.register_model('Activity', self.activity)


    def test_title_201(self):
        self.parser_201.iati_activities__iati_activity__title(self.title)

        title = self.parser_201.get_model('Title')
        self.assertTrue(title.activity == self.activity)

        self.parser_201.iati_activities__iati_activity__title__narrative(self.narrative)
        narrative = self.parser_201.get_model('TitleNarrative')
        self.assertTrue(narrative.related_object == title)

        # TODO: refactor so this isnt nescessary
        title = self.parser_201.pop_model('Title')
        
    def test_title_duplicate(self):
        """
        Duplicates are not allowed
        """
        self.parser_201.iati_activities__iati_activity__title(self.title)

        with self.assertRaises(Exception):
            self.parser_201.iati_activities__iati_activity__title(self.title)

        # TODO: refactor so this isnt nescessary
        title = self.parser_201.pop_model('Title')

    def test_title_activity_constraint(self):
        """
        An activity should not be parseable without a title
        """
        # TODO: problem because OneToOne is on Title, which is a workaround for django's poor admin handling of oneToOne relations
        

    def test_title_105(self):
        self.title.text = "random text"
        self.parser_105.iati_activities__iati_activity__title(self.title)

        title = self.parser_105.get_model('Title')
        narrative = self.parser_105.get_model('TitleNarrative')

        self.assertTrue(title.activity == self.activity)
        self.assertTrue(narrative.related_object == title)

        # TODO: refactor so this isnt nescessary
        title = self.parser_201.pop_model('Title')

    def test_second_title_as_narrative_105(self):
        self.title.text = "random text"
        second_title = E('title', 'second title')

        self.parser_105.iati_activities__iati_activity__title(self.title)

        title = self.parser_105.get_model('Title')
        narrative = self.parser_105.get_model('TitleNarrative')

        self.parser_105.iati_activities__iati_activity__title(second_title)
        second_narrative = self.parser_105.get_model('TitleNarrative')

        self.assertTrue(title.activity == self.activity)
        self.assertTrue(narrative.related_object == title)
        self.assertEqual(narrative.content, 'random text')
        self.assertEqual(second_narrative.content, 'second title')

        # TODO: refactor so this isnt nescessary
        title = self.parser_201.pop_model('Title')

        
class DescriptionTestCase(ParserSetupTestCase):
    def setUp(self):
        self.iati_201 = copy_xml_tree(self.iati_201)

        self.description = E('description', )
        self.narrative = E('narrative', "random text")

        self.activity = build_activity(version="2.01")
        self.parser_201.register_model('Activity', self.activity)
        self.parser_105.register_model('Activity', self.activity)

    def test_description_201(self):
        self.parser_201.iati_activities__iati_activity__description(self.description)
        description = self.parser_201.get_model('Description')

        self.assertTrue(description.activity == self.activity)

        self.parser_201.iati_activities__iati_activity__description__narrative(self.narrative)
        narrative = self.parser_201.get_model('DescriptionNarrative')

        self.assertTrue(narrative.related_object == description)

    def test_description_105(self):
        self.description.text = "random text"
        self.parser_105.iati_activities__iati_activity__description(self.description)

        description = self.parser_105.get_model('Description')
        narrative = self.parser_105.get_model('DescriptionNarrative')

        self.assertTrue(description.activity == self.activity)
        self.assertTrue(narrative.related_object == description)

class OtherIdentifierTestCase(ParserSetupTestCase):
    """
    2.01: Freetext support of the other-identifier was removed. A new other-identifier/@ref was added as a replacement.
    2.01: A new attribute other-identifier/@type was added, to be used with new code list OtherIdentifierType.
    2.01: The other-identifier/@owner-ref and other-identifier/@owner-name attributes were removed.
    2.01: The owner-org child element was added.
    """
    def setUp(self):
        self.iati_201 = copy_xml_tree(self.iati_201)

        self.attrs_201 = {
            "ref": "Some-ref",
            "type": "A1",
        }
        self.attrs_105 = {
            "owner-ref": "Some-owner-ref",
            "owner-name": "Some name",
        }
        self.owner_org_xml = {
            "ref": "Some-owner-ref",
        }

        self.other_identifier_201 = E('other-identifier', self.attrs_201)
        self.owner_org = E('owner-org', self.owner_org_xml)
        self.other_identifier_105 = E('other-identifier', self.attrs_105, "Some-ref")
        self.narrative = E('narrative', "Some name")

        self.activity = build_activity(version="2.01")
        self.parser_201.register_model('Activity', self.activity)
        self.parser_105.register_model('Activity', self.activity)

    def test_other_identifier_201(self):
        """
        Also tests the owner_org element (same model) along with its narrative
        """
        self.parser_201.iati_activities__iati_activity__other_identifier(self.other_identifier_201)
        other_identifier = self.parser_201.get_model('OtherIdentifier')

        self.assertTrue(other_identifier.activity == self.activity)
        self.assertTrue(other_identifier.identifier == self.attrs_201['ref'])
        self.assertTrue(other_identifier.type.code == self.attrs_201['type'])

        self.parser_201.iati_activities__iati_activity__other_identifier__owner_org(self.owner_org)
        other_identifier = self.parser_201.get_model('OtherIdentifier')

        self.assertTrue(other_identifier.owner_ref == self.owner_org_xml['ref'])

        self.parser_201.iati_activities__iati_activity__other_identifier__owner_org__narrative(self.narrative)
        narrative = self.parser_201.get_model('OtherIdentifierNarrative')

        self.assertTrue(narrative.related_object == other_identifier)

    def test_other_identifier_105(self):
        """
        If other-identifier is present then either @owner-ref or @owner-name must be present
        """
        self.parser_105.iati_activities__iati_activity__other_identifier(self.other_identifier_105)
        other_identifier = self.parser_105.get_model('OtherIdentifier')

        self.assertTrue(other_identifier.activity == self.activity)
        self.assertTrue(other_identifier.identifier == "Some-ref")
        self.assertTrue(other_identifier.owner_ref == self.owner_org_xml['ref'])

        narrative = self.parser_105.get_model('OtherIdentifierNarrative')
        self.assertTrue(narrative.related_object == other_identifier)

class NarrativeTestCase(ParserSetupTestCase):
    """
    Added in 2.01
    """
    def setUp(self):
        self.iati_201 = copy_xml_tree(self.iati_201)

        # default narrative model fields
        self.defaults = {
            "language": "en",
        }
        self.test_text = "this text should match in the tests"

        self.narrative = E('narrative', self.test_text)
        # This could be any object for testing
        self.related_object = build_activity()
        self.parser_201.register_model('Activity', self.related_object)
        self.parser_105.register_model('Activity', self.related_object)

    def test_addForeignKeyDefaultNarrative(self):
        """
        Given an arbitrary foreign key, the narrative should be created and be queryable using default assumed values (language)
        """
        self.parser_201.add_narrative(self.narrative, self.related_object)
        narrative = self.parser_201.get_model('ActivityNarrative')

        self.assertTrue(narrative.related_object == self.related_object)
        self.assertTrue(narrative.content == self.test_text)
        self.assertTrue(narrative.language.code == self.defaults["language"])

    def test_addForeignKeyNonDefaultLanguageNarrative(self):
        """
        The narrative should change its language parameter based on the xml:lang element 
        """
        self.narrative.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "fr" # ISO 639-1:2002

        self.parser_201.add_narrative(self.narrative, self.related_object)
        narrative = self.parser_201.get_model('ActivityNarrative')

        self.assertTrue(narrative.language.code == "fr")


# Todo: after organization implementation
class OrganisationTestCase(ParserSetupTestCase):
    pass


class ActivityReportingOrganisationTestCase(ParserSetupTestCase):
    """
    2.01: Freetext is no longer allowed with this element. It should now be declared with the new child narrative element.
    1.04: The secondary-publisher was introduced in 1.04.
    """

    def setUp(self):
        self.iati_201 = copy_xml_tree(self.iati_201) # sample attributes on iati-activity xml
        self.attrs = {
            "ref": "GB-COH-03580586",
            "type": '40',
            "secondary-reporter": "0",
            "primary_name": "primary_name"
        }

        self.reporting_org = E('reporting-org', E('narrative', "primary_name"), **self.attrs)

    def test_reporting_organisation_not_parsed_yet(self):
        """
        Check element is parsed correctly, excluding narratives when organisation is not in the organisation API. This results in the organisation field being empty
        """
        activity = build_activity(version="2.01")
        self.parser_201.register_model('Activity', activity)

        self.parser_201.iati_activities__iati_activity__reporting_org(self.reporting_org)

        reporting_organisation = self.parser_201.get_model('ActivityReportingOrganisation')

        self.assertTrue(reporting_organisation.ref == self.attrs["ref"])
        self.assertTrue(reporting_organisation.type.code == self.attrs["type"])
        self.assertTrue(reporting_organisation.activity == activity)
        self.assertTrue(reporting_organisation.secondary_reporter == bool(int(self.attrs["secondary-reporter"])))

        # should create an organisation
        organisation = self.parser_201.get_model('Organisation')
        self.assertEqual(organisation.id, self.attrs["ref"])
        self.assertEqual(organisation.organisation_identifier, self.attrs["ref"])
        self.assertEqual(organisation.primary_name, self.attrs["primary_name"])
        self.assertEqual(organisation.reported_in_iati, False)

        self.assertEqual(reporting_organisation.organisation, organisation)

        organisation_narrative = self.parser_201.get_model('OrganisationNameNarrative')
        self.assertEqual(organisation_narrative.content, self.attrs["primary_name"])


    def test_reporting_organisation_already_parsed(self):
        """
        Check complete element is parsed correctly, excluding narratives when the organisation is available in the Organisation standard (and hence is pared)
        """
        activity = build_activity(version="2.01")

        test_organisation = iati_factory.OrganisationFactory.build()
        test_organisation.save()

        self.parser_201.register_model('Activity', activity)
        self.parser_201.register_model('Organisation', test_organisation)

        self.parser_201.iati_activities__iati_activity__reporting_org(self.reporting_org)

        # activity = self.parser_201.get_model('Activity')
        organisation = self.parser_201.get_model('Organisation')
        reporting_organisation = self.parser_201.get_model('ActivityReportingOrganisation')

        self.assertTrue(reporting_organisation.activity == activity)
        self.assertTrue(reporting_organisation.organisation.id == test_organisation.id)
        self.assertTrue(reporting_organisation.type.code == self.attrs["type"])
        self.assertTrue(reporting_organisation.secondary_reporter == bool(int(self.attrs["secondary-reporter"])))

    @skip('NotImplemented')
    def test_reporting_organisation_narrative(self):
        raise NotImplementedError()


class ActivityParticipatingOrganisationTestCase(ParserSetupTestCase):
    """
    2.01: Freetext is no longer allowed with this element. It should now be declared with the new child narrative element.
    2.01: The OrganisationRole codelist was changed to numeric codes
    """

    def setUp(self):
        self.iati_201 = copy_xml_tree(self.iati_201) # sample attributes on iati-activity xml

        self.attrs_201 = {
            "ref": "GB-COH-03580586",
            "type": '40',
            "role": "1",
        }
        self.attrs_105 = copy.deepcopy(self.attrs_201)
        self.attrs_105['role'] = "Funding" 

        self.participating_org_201 = E('participating-org', **self.attrs_201)
        self.participating_org_105 = E('participating-org', "some text", **self.attrs_105)

        self.narrative = E('narrative', "random text")

    def test_participating_organisation_not_parsed_yet_201(self):
        """
        Check element is parsed correctly, excluding narratives when organisation is not in the organisation API. This results in the organisation field being empty
        """
        activity = build_activity(version="2.01")
        self.parser_201.register_model('Activity', activity)

        self.parser_201.iati_activities__iati_activity__participating_org(self.participating_org_201)
        participating_organisation = self.parser_201.get_model('ActivityParticipatingOrganisation')

        self.assertTrue(participating_organisation.ref == self.attrs_201["ref"])
        self.assertTrue(participating_organisation.type.code == self.attrs_201["type"])
        self.assertTrue(participating_organisation.activity == activity)
        self.assertTrue(participating_organisation.organisation == None)
        self.assertTrue(participating_organisation.role.code == self.attrs_201["role"])

        self.parser_201.iati_activities__iati_activity__participating_org__narrative(self.narrative)
        narrative = self.parser_201.get_model('ActivityParticipatingOrganisationNarrative')
        self.assertTrue(narrative.related_object == participating_organisation)
        self.assertTrue(participating_organisation.primary_name == 'random text')

    def test_participating_organisation_already_parsed_201(self):
        """
        Check complete element is parsed correctly, excluding narratives when the organisation is available in the Organisation standard (and hence is pared)
        """
        activity = build_activity(version="2.01")

        test_organisation = iati_factory.OrganisationFactory.build()
        test_organisation.save()

        self.parser_201.register_model('Activity', activity)
        self.parser_201.register_model('Organisation', test_organisation)

        self.parser_201.iati_activities__iati_activity__participating_org(self.participating_org_201)

        # activity = self.parser_201.get_model('Activity')
        organisation = self.parser_201.get_model('Organisation')
        participating_organisation = self.parser_201.get_model('ActivityParticipatingOrganisation')

        self.assertTrue(participating_organisation.activity == activity)
        self.assertTrue(participating_organisation.organisation.id == test_organisation.id)
        self.assertTrue(participating_organisation.type.code == self.attrs_201["type"])
        self.assertTrue(participating_organisation.role.code == self.attrs_201["role"])

    def test_participating_organisation_not_parsed_yet_105(self):
        """
        With alternate organisation role codelists
        """
        activity = build_activity(version="1.05")
        self.parser_105.register_model('Activity', activity)

        self.parser_105.iati_activities__iati_activity__participating_org(self.participating_org_105)

        participating_organisation = self.parser_105.get_model('ActivityParticipatingOrganisation')

        self.assertTrue(participating_organisation.ref == self.attrs_105["ref"])
        self.assertTrue(participating_organisation.type.code == self.attrs_105["type"])
        self.assertTrue(participating_organisation.activity == activity)
        self.assertTrue(participating_organisation.organisation == None)
        self.assertTrue(participating_organisation.role.code == self.attrs_201["role"])

        narrative = self.parser_105.get_model('ActivityParticipatingOrganisationNarrative')
        self.assertTrue(narrative.related_object == participating_organisation)
        self.assertTrue(participating_organisation.primary_name == 'some text')

    def test_participating_organisation_already_parsed_105(self):
        """
        Check complete element is parsed correctly, 
        excluding narratives when the organisation is available in the Organisation standard (and hence is pared)
        """
        activity = build_activity(version="1.05")

        test_organisation = iati_factory.OrganisationFactory.build()
        test_organisation.save()

        self.parser_105.register_model('Activity', activity)
        self.parser_105.register_model('Organisation', test_organisation)

        self.parser_105.iati_activities__iati_activity__participating_org(self.participating_org_105)

        # activity = self.parser_105.get_model('Activity')
        organisation = self.parser_105.get_model('Organisation')
        participating_organisation = self.parser_105.get_model('ActivityParticipatingOrganisation')

        self.assertTrue(participating_organisation.activity == activity)
        self.assertTrue(participating_organisation.organisation.id == test_organisation.id)
        self.assertTrue(participating_organisation.type.code == self.attrs_105["type"])
        self.assertTrue(participating_organisation.role.code == self.attrs_201["role"])

    def test_primary_name_is_set_105(self):
        """
        Test the primary name in order to work around ref uniqueness is set correctly for the first narrative only
        """
        activity = build_activity(version="1.05")
        self.parser_105.register_model('Activity', activity)

        self.parser_105.iati_activities__iati_activity__participating_org(self.participating_org_105)

        participating_organisation = self.parser_105.get_model('ActivityParticipatingOrganisation')

        self.assertEqual(participating_organisation.primary_name, "some text")

class ActivityDateTestCase(ParserSetupTestCase):
    """
    2.01: Freetext is no longer allowed with this element. It should now be declared with the new child narrative element.
    2.01: The ActivityDateType codelist was changed to numeric codes
    """

    def setUp(self):
        self.iati_201 = copy_xml_tree(self.iati_201) # sample attributes on iati-activity xml

        self.attrs_201 = {
            "type": "1", # planned-start
            "iso-date": datetime.datetime.now().isoformat(' '),
        }
        self.attrs_105 = copy.deepcopy(self.attrs_201)
        self.attrs_105["type"] = "start-planned"

        self.activity_date_201 = E('activity-date', **self.attrs_201)
        self.activity_date_105 = E('activity-date', 'Some description', **self.attrs_105)

        self.narrative = E('narrative', "Some description")

        self.activity = build_activity(version="2.01")
        self.parser_201.register_model('Activity', self.activity)
        self.parser_105.register_model('Activity', self.activity)

    def test_activity_date_201(self):
        """
        Along with its narrative(s)
        """
        self.parser_201.iati_activities__iati_activity__activity_date(self.activity_date_201)
        activity_date = self.parser_201.get_model('ActivityDate')

        self.assertTrue(activity_date.activity == self.activity)
        self.assertTrue(str(activity_date.iso_date) == self.attrs_201['iso-date'])
        self.assertTrue(activity_date.type.code == self.attrs_201['type'])

        self.parser_201.iati_activities__iati_activity__activity_date__narrative(self.narrative)
        narrative = self.parser_201.get_model('ActivityDateNarrative')

        self.assertTrue(narrative.related_object == activity_date)

    def test_activity_date_105(self):
        """
        If other-identifier is present then either @owner-ref or @owner-name must be present
        """
        self.parser_105.iati_activities__iati_activity__activity_date(self.activity_date_105)
        activity_date = self.parser_105.get_model('ActivityDate')

        self.assertTrue(activity_date.activity == self.activity)
        self.assertTrue(str(activity_date.iso_date) == self.attrs_201['iso-date'])
        self.assertTrue(activity_date.type.code == self.attrs_201['type'])

        narrative = self.parser_105.get_model('ActivityDateNarrative')
        self.assertTrue(narrative.related_object == activity_date)

class ContactInfoTestCase(ParserSetupTestCase):
    """
    2.01:  The optional contact-info/department element was added.
    1.03: Added the optional contact-info/website element.
    1.03: Added the optional contact-info/@type attribute.
    1.03: Changed the following subelements of contact-info to allow multiple-language versions explicitly (no change to parsing; purely semantic):
        * organisation
        * person-name
        * job-title
        * mailing-address
    """

    def setUp(self):
        self.iati_201 = copy_xml_tree(self.iati_201) # sample attributes on iati-activity xml

        self.attrs = {
            "type": "1", # General Enquiries
        }

        self.contact_info = E('contact-info', **self.attrs)
        # self.contact_info = E('activity-date', 'Some description', **self.attrs_105)
        self.narrative = E('narrative', "Some description")

        self.activity = build_activity(version="2.01")
        self.test_contact_info = iati_factory.ContactInfoFactory.build()
        self.test_contact_info.save()

        self.parser_201.register_model('Activity', self.activity)
        self.parser_201.register_model('ContactInfo', self.test_contact_info)

        self.parser_105.register_model('Activity', self.activity)
        self.parser_105.register_model('ContactInfo', self.test_contact_info)

    def test_contact_info_201(self):
        """
        Only defines the type field
        """
        self.parser_201.iati_activities__iati_activity__contact_info(self.contact_info)
        contact_info = self.parser_201.get_model('ContactInfo')

        self.assertEqual(contact_info.activity, self.activity, 'contact info activity should match')
        self.assertEqual(contact_info.type.code, self.attrs['type'], 'contact info type code should match')

    def test_contact_info_organisation_201(self):
        """
        Along with narrative
        """
        contact_organisation = E('organisation', **self.attrs)
        self.parser_201.iati_activities__iati_activity__contact_info__organisation(contact_organisation)
        contact_info_organisation = self.parser_201.get_model('ContactInfoOrganisation')

        self.assertTrue(contact_info_organisation.contact_info == self.test_contact_info)

        self.parser_201.iati_activities__iati_activity__contact_info__organisation__narrative(self.narrative)
        narrative = self.parser_201.get_model('ContactInfoOrganisationNarrative')
        self.assertTrue(narrative.related_object == contact_info_organisation)

    def test_contact_info_organisation_105(self):
        """
        Along with narrative
        """
        contact_organisation = E('organisation', 'some description')
        self.parser_105.iati_activities__iati_activity__contact_info__organisation(contact_organisation)
        contact_info_organisation = self.parser_105.get_model('ContactInfoOrganisation')

        self.assertTrue(contact_info_organisation.contact_info == self.test_contact_info)
        narrative = self.parser_105.get_model('ContactInfoOrganisationNarrative')
        self.assertTrue(narrative.related_object == contact_info_organisation)

    def test_contact_info_department(self):
        """
        Along with narrative
        """
        contact_department = E('department', **self.attrs)
        self.parser_201.iati_activities__iati_activity__contact_info__department(contact_department)
        contact_info_department = self.parser_201.get_model('ContactInfoDepartment')

        self.assertTrue(contact_info_department.contact_info == self.test_contact_info)

        self.parser_201.iati_activities__iati_activity__contact_info__department__narrative(self.narrative)
        narrative = self.parser_201.get_model('ContactInfoDepartmentNarrative')
        self.assertTrue(narrative.related_object == contact_info_department)

    def test_contact_info_department_105(self):
        """
        Along with narrative
        """
        contact_department = E('department', 'some description')
        self.parser_105.iati_activities__iati_activity__contact_info__department(contact_department)
        contact_info_department = self.parser_105.get_model('ContactInfoDepartment')

        self.assertTrue(contact_info_department.contact_info == self.test_contact_info)
        narrative = self.parser_105.get_model('ContactInfoDepartmentNarrative')

    def test_contact_info_person_name(self):
        """
        Along with narrative
        """
        contact_person_name = E('person-name', **self.attrs)
        self.parser_201.iati_activities__iati_activity__contact_info__person_name(contact_person_name)
        contact_info_person_name = self.parser_201.get_model('ContactInfoPersonName')

        self.assertTrue(contact_info_person_name.contact_info == self.test_contact_info)

        self.parser_201.iati_activities__iati_activity__contact_info__person_name__narrative(self.narrative)
        narrative = self.parser_201.get_model('ContactInfoPersonNameNarrative')
        self.assertTrue(narrative.related_object == contact_info_person_name)

    def test_contact_info_person_name_105(self):
        """
        Along with narrative
        """
        contact_person_name = E('person_name', 'some description')
        self.parser_105.iati_activities__iati_activity__contact_info__person_name(contact_person_name)
        contact_info_person_name = self.parser_105.get_model('ContactInfoPersonName')

        self.assertTrue(contact_info_person_name.contact_info == self.test_contact_info)
        narrative = self.parser_105.get_model('ContactInfoPersonNameNarrative')

    def test_contact_info_job_title(self):
        """
        Along with narrative
        """
        contact_job_title = E('job-title', **self.attrs)
        self.parser_201.iati_activities__iati_activity__contact_info__job_title(contact_job_title)
        contact_info_job_title = self.parser_201.get_model('ContactInfoJobTitle')

        self.assertTrue(contact_info_job_title.contact_info == self.test_contact_info)

        self.parser_201.iati_activities__iati_activity__contact_info__job_title__narrative(self.narrative)
        narrative = self.parser_201.get_model('ContactInfoJobTitleNarrative')
        self.assertTrue(narrative.related_object == contact_info_job_title)

    def test_contact_info_job_title_105(self):
        """
        Along with narrative
        """
        contact_job_title = E('job_title', 'some description')
        self.parser_105.iati_activities__iati_activity__contact_info__job_title(contact_job_title)
        contact_info_job_title = self.parser_105.get_model('ContactInfoJobTitle')

        self.assertTrue(contact_info_job_title.contact_info == self.test_contact_info)
        narrative = self.parser_105.get_model('ContactInfoJobTitleNarrative')

    def test_contact_info_telephone(self):
        contact_telephone = E('telephone', "some telephone")
        self.parser_201.iati_activities__iati_activity__contact_info__telephone(contact_telephone)
        contact_info = self.parser_201.get_model('ContactInfo')

        self.assertTrue(contact_info.telephone == "some telephone")

    def test_contact_info_email(self):
        contact_email = E('email', "some email")
        self.parser_201.iati_activities__iati_activity__contact_info__email(contact_email)
        contact_info = self.parser_201.get_model('ContactInfo')

        self.assertTrue(contact_info.email == "some email")

    def test_contact_info_website(self):
        contact_website = E('website', "some website")
        self.parser_201.iati_activities__iati_activity__contact_info__website(contact_website)
        contact_info = self.parser_201.get_model('ContactInfo')

        self.assertTrue(contact_info.website == "some website")

    def test_contact_info_mailing_address(self):
        """
        Along with narrative
        """
        contact_mailing_address = E('mailing-address', **self.attrs)
        self.parser_201.iati_activities__iati_activity__contact_info__mailing_address(contact_mailing_address)
        contact_info_mailing_address = self.parser_201.get_model('ContactInfoMailingAddress')

        self.assertTrue(contact_info_mailing_address.contact_info == self.test_contact_info)

        self.parser_201.iati_activities__iati_activity__contact_info__mailing_address__narrative(self.narrative)
        narrative = self.parser_201.get_model('ContactInfoMailingAddressNarrative')
        self.assertTrue(narrative.related_object == contact_info_mailing_address)

    def test_contact_info_mailing_address_105(self):
        """
        Along with narrative
        """
        contact_mailing_address = E('mailing_address', 'some description')
        self.parser_105.iati_activities__iati_activity__contact_info__mailing_address(contact_mailing_address)
        contact_info_mailing_address = self.parser_105.get_model('ContactInfoMailingAddress')

        self.assertTrue(contact_info_mailing_address.contact_info == self.test_contact_info)

        narrative = self.parser_105.get_model('ContactInfoMailingAddressNarrative')
        self.assertTrue(narrative.related_object == contact_info_mailing_address)

class RecipientCountryTestCase(ParserSetupTestCase):
    """
    2.01: Freetext is no longer allowed with this element. It should now be declared with the new child narrative element, but only in particular use-cases.
    1.03: Where used, the @percentage attribute is now designated as a decimal value and no longer as a positive Integer
    """

    def setUp(self):
        self.iati_201 = copy_xml_tree(self.iati_201) # sample attributes on iati-activity xml

        self.attrs = {
            "code": "AF",
            "percentage": "50.5",
        }

        self.recipient_country = E('recipient-country', **self.attrs)
        self.narrative = E('narrative', "Some description")

        self.activity = build_activity(version="2.01")
        self.parser_201.register_model('Activity', self.activity)
        self.parser_105.register_model('Activity', self.activity)

    def test_recipient_country_201(self):
        """
        Along with its narrative(s)
        """
        self.parser_201.iati_activities__iati_activity__recipient_country(self.recipient_country)
        recipient_country = self.parser_201.get_model('ActivityRecipientCountry')

        self.assertTrue(recipient_country.activity == self.activity)
        self.assertTrue(recipient_country.country.code == self.attrs['code'])
        self.assertTrue(recipient_country.percentage == self.attrs['percentage'])

        # TODO: needs narrative?

class RecipientRegionTestCase(ParserSetupTestCase):
    """
    2.01: Freetext is no longer allowed with this element. It should now be declared with the new child narrative element, but only in particular use-cases.
    1.03: Where used, the @percentage attribute is now designated as a decimal value and no longer as a positive Integer
    """

    def setUp(self):
        self.iati_201 = copy_xml_tree(self.iati_201) # sample attributes on iati-activity xml

        self.attrs = {
            "code": "89", # Europe, regional
            "vocabulary": "1", # OECD-DAC
            "percentage": "50.5",
        }

        self.recipient_region = E('recipient-region', **self.attrs)
        self.narrative = E('narrative', "Some description")

        self.activity = build_activity(version="2.01")
        self.parser_201.register_model('Activity', self.activity)
        self.parser_105.register_model('Activity', self.activity)

    def test_recipient_region_201(self):
        """
        Along with its narrative(s)
        """
        self.parser_201.iati_activities__iati_activity__recipient_region(self.recipient_region)
        recipient_region = self.parser_201.get_model('ActivityRecipientRegion')

        self.assertTrue(recipient_region.activity == self.activity)
        self.assertTrue(recipient_region.region.code == self.attrs['code'])
        self.assertTrue(recipient_region.percentage == self.attrs['percentage'])
        self.assertTrue(recipient_region.vocabulary.code == self.attrs['vocabulary'])

        # TODO: needs narrative?

    def test_recipient_region_201_defaults(self):
        """
        Check default vocabulary is set accordingly
        """
        del self.recipient_region.attrib['vocabulary']
        self.parser_201.iati_activities__iati_activity__recipient_region(self.recipient_region)
        recipient_region = self.parser_201.get_model('ActivityRecipientRegion')

        self.assertTrue(recipient_region.vocabulary.code == "1")

class ActivityLocationTestCase(ParserSetupTestCase):
    """
    2.01: The following child elements were removed: coordinates; gazetteer-entry; location-type.
    2.01: The @percentage attribute was removed.

    1.04: Note that major changes were made to the subelements of location in version 1.04.

    For more information refer to:
    * the 1.04 location changes overview guidance
    * the Activities Schema Changelog (or the individual subemelement pages)
    1.04: The @ref attribute was introduced to provide a cross reference that a publisher can use to link back to their own internal system.
    1.04: The @percentage attribute was deemed unworkable and deprecated in 1.04
    1.03: Where used, the @percentage attribute is now designated as a decimal value and no longer as a positive Integer
    """
    def setUp(self):
        self.iati_201 = copy_xml_tree(self.iati_201) # sample attributes on iati-activity xml

        self.attrs_201 = {
            "ref": "some-ref", # Europe, regional
        }
        self.attrs_105 = copy.deepcopy(self.attrs_201)
        self.attrs_105['percentage'] = '50.2'

        self.location_201 = E('location', **self.attrs_201)
        self.location_105 = E('location', "Some description", **self.attrs_105)
        self.location_103 = E('location', "Some description", **self.attrs_105)
        self.narrative = E('narrative', "Some description")

        self.activity = build_activity(version="2.01")
        self.test_location = iati_factory.LocationFactory.build()
        # self.test_location.save()

        self.parser_201.register_model('Activity', self.activity)
        self.parser_201.register_model('Location', self.test_location)
        self.parser_105.register_model('Activity', self.activity)
        self.parser_105.register_model('Location', self.test_location)
        self.parser_103.register_model('Activity', self.activity)
        self.parser_103.register_model('Location', self.test_location)

    def test_location_201(self):
        self.parser_201.iati_activities__iati_activity__location(self.location_201)
        location = self.parser_201.get_model('Location')

        self.assertTrue(location.activity == self.activity)
        self.assertTrue(location.ref == self.attrs_201['ref'])

    def test_location_reach_201(self):
        location_reach = E('location-reach', code="1") # Activity
        self.parser_201.iati_activities__iati_activity__location__location_reach(location_reach)
        location = self.parser_201.get_model('Location')

        self.assertTrue(location.location_reach.code == "1")

    def test_location_id_201(self):
        location_id = E('location-id', code="test", vocabulary="A1") # Global Administrative Unit layers
        self.parser_201.iati_activities__iati_activity__location__location_id(location_id)
        location = self.parser_201.get_model('Location')

        self.assertTrue(location.location_id_code == "test")
        self.assertTrue(location.location_id_vocabulary.code == "A1")

    def test_location_name_201(self):
        """
        Including narratives
        """
        location_name = E('name')
        self.parser_201.iati_activities__iati_activity__location__name(location_name)
        location_name = self.parser_201.get_model('LocationName')

        self.assertTrue(location_name.location == self.test_location)

        self.parser_201.iati_activities__iati_activity__location__name__narrative(self.narrative)
        narrative = self.parser_201.get_model('LocationNameNarrative')
        self.assertTrue(narrative.related_object == location_name)

    def test_location_name_105(self):
        location_name = E('name', "some text")
        self.parser_105.iati_activities__iati_activity__location__name(location_name)
        location_name = self.parser_105.get_model('LocationName')

        self.assertTrue(location_name.location == self.test_location)
        narrative = self.parser_105.get_model('LocationNameNarrative')
        self.assertTrue(narrative.related_object == location_name)

    def test_location_description_201(self):
        """
        Including narratives
        """
        location_description = E('description')
        self.parser_201.iati_activities__iati_activity__location__description(location_description)
        location_description = self.parser_201.get_model('LocationDescription')

        self.assertTrue(location_description.location == self.test_location)

        self.parser_201.iati_activities__iati_activity__location__description__narrative(self.narrative)
        narrative = self.parser_201.get_model('LocationDescriptionNarrative')
        self.assertTrue(narrative.related_object == location_description)

    def test_location_activity_description_201(self):
        """
        Including narratives
        """
        activity_description = E('activity-description')
        self.parser_201.iati_activities__iati_activity__location__activity_description(activity_description)
        activity_description = self.parser_201.get_model('LocationActivityDescription')

        self.assertTrue(activity_description.location == self.test_location)

        self.parser_201.iati_activities__iati_activity__location__activity_description__narrative(self.narrative)
        narrative = self.parser_201.get_model('LocationActivityDescriptionNarrative')
        self.assertTrue(narrative.related_object == activity_description)

    def test_location_administrative_201(self):
        administrative = E('administrative', code="test", vocabulary="A1", level="1") # Global Administrative Unit layers
        self.parser_201.iati_activities__iati_activity__location__administrative(administrative)
        location_administrative = self.parser_201.get_model('LocationAdministrative')

        self.assertTrue(location_administrative.code == "test")
        self.assertTrue(location_administrative.vocabulary.code == "A1")
        self.assertTrue(location_administrative.level == "1")

    def test_location_administrative_103(self):
        administrative = E('administrative', country="test", adm1="test", adm2="test") 
        self.parser_103.iati_activities__iati_activity__location__administrative(administrative)

        # adm2
        administrative = self.parser_103.pop_model('LocationAdministrative')
        self.assertTrue(administrative.code == "test")
        self.assertTrue(administrative.vocabulary.code == "A2")
        self.assertTrue(administrative.level == "2")

        # adm1
        administrative = self.parser_103.pop_model('LocationAdministrative')
        self.assertTrue(administrative.code == "test")
        self.assertTrue(administrative.vocabulary.code == "A2")
        self.assertTrue(administrative.level == "1")

        # country
        administrative = self.parser_103.pop_model('LocationAdministrative')
        self.assertTrue(administrative.code == "test")
        self.assertTrue(administrative.vocabulary.code == "A4")

    def test_location_point_201(self):
        point = E('point', srsName="http://www.opengis.net/def/crs/EPSG/0/4326") # Global Point Unit layers
        self.parser_201.iati_activities__iati_activity__location__point(point)
        location = self.parser_201.get_model('Location')

        self.assertTrue(location.point_srs_name == "http://www.opengis.net/def/crs/EPSG/0/4326")

    def test_location_pos_pos_valid_latlong_201(self):
        """
        test with valid latlong
        """
        pos = E('pos', '31.616944 65.716944')
        self.parser_201.iati_activities__iati_activity__location__point__pos(pos)
        location = self.parser_201.get_model('Location')
        # Geo point = longlat
        self.assertTrue(location.point_pos.coords == (65.716944, 31.616944))

    # TODO : test for latlong validation
    # def test_location_pos_pos_invalid_latlong_201(self):
    #     pos = E('pos', '91.616944 328392189031283.716944')
    #     with self.assertRaises(ValidationError):
    #         self.parser_201.iati_activities__iati_activity__location__point__pos(pos)

    def test_location_exactness_201(self):
        exactness = E('exactness', code="1") # Exact
        self.parser_201.iati_activities__iati_activity__location__exactness(exactness)
        location = self.parser_201.get_model('Location')

        self.assertTrue(location.exactness.code == "1")

    def test_location_location_class_201(self):
        location_class = E('location-class', code="1") # Administrative region
        self.parser_201.iati_activities__iati_activity__location__location_class(location_class)
        location = self.parser_201.get_model('Location')

        self.assertTrue(location.location_class.code == "1")

    def test_location_feature_designation_201(self):
        feature_designation = E('feature-designation', code="AIRQ") # Abandoned airfield
        self.parser_201.iati_activities__iati_activity__location__feature_designation(feature_designation)
        location = self.parser_201.get_model('Location')

        self.assertTrue(location.feature_designation.code == "AIRQ")

    def test_location_coordinates_103(self):
        coordinates = E('pos', latitude='31.616944', longitude='65.716944', precision='1') # exact
        self.parser_103.iati_activities__iati_activity__location__coordinates(coordinates)
        location = self.parser_103.get_model('Location')

        self.assertTrue(location.point_srs_name == "http://www.opengis.net/def/crs/EPSG/0/4326")
        # Geodjango Location = longlat
        self.assertTrue(location.point_pos.coords == (65.716944, 31.616944))
        self.assertTrue(location.exactness.code == "1")

    def test_location_coordinates_transform_code_103(self):
        """
        A precision value greater than 1, should be mapped to 2, see:
        http://iatistandard.org/201/codelists/GeographicExactness/
        http://iatistandard.org/201/codelists/GeographicalPrecision/
        """
        coordinates = E('pos', latitude='31.616944', longitude='65.716944', precision='5') # exact
        self.parser_103.iati_activities__iati_activity__location__coordinates(coordinates)
        location = self.parser_103.get_model('Location')

        self.assertTrue(location.exactness.code == "2")

    def test_location_gazetteer_103(self):
        """
        Map to 201 location-id field
        """
        props = {
            "gazetteer-ref": "OSM"
        }
        gazetteer = E('gazetteer-entry', "some code", **props) # Geonames.org
        self.parser_103.iati_activities__iati_activity__location__gazetteer_entry(gazetteer)
        location = self.parser_103.get_model('Location')
        
        self.assertTrue(location.location_id_code == "some code")
        self.assertTrue(location.location_id_vocabulary.code == "G2")

    def test_location_gazetteer_deprecated_field_103(self):
        """
        Test parsing with gazetteer-ref: 2 throws error
        """
        props = {
            "gazetteer-ref": "2"
        }
        gazetteer = E('gazetteer-entry', "some code", **props) # Geonames.org

        with self.assertRaises(Exception):
            self.parser_103.iati_activities__iati_activity__location__gazetteer_entry(gazetteer)

    def test_location_location_type_103(self):
        """
        Maps to 201 feature_designation field
        """
        location_type = E('location-type', code="AIRQ") # Abandoned airfield
        self.parser_103.iati_activities__iati_activity__location__location_type(location_type)
        location = self.parser_103.get_model('Location')

        self.assertTrue(location.feature_designation.code == "AIRQ")

class SectorTestCase(ParserSetupTestCase):
    """
    1.03: Where used, the @percentage attribute is now designated as a decimal value and no longer as a positive Integer
    """

    def setUp(self):
        self.iati_201 = copy_xml_tree(self.iati_201) # sample attributes on iati-activity xml

        self.attrs = {
            "code": "11110", # Education Policy and administrative management
            "vocabulary": "1", # OECD-DAC-5
            "percentage": "50.5",
        }

        self.sector = E('sector', **self.attrs)
        self.narrative = E('narrative', "Some description")

        self.activity = build_activity(version="2.01")
        self.parser_201.register_model('Activity', self.activity)
        self.parser_105.register_model('Activity', self.activity)

    def test_sector_201(self):
        """
        Along with its narrative(s)
        """
        self.parser_201.iati_activities__iati_activity__sector(self.sector)
        sector = self.parser_201.get_model('ActivitySector')

        self.assertTrue(sector.activity == self.activity)
        self.assertTrue(sector.sector.code == self.attrs['code'])
        self.assertTrue(sector.percentage == self.attrs['percentage'])
        self.assertTrue(sector.vocabulary.code == self.attrs['vocabulary'])

        # TODO: needs narrative?

    def test_sector_201_defaults(self):
        """
        Check default vocabulary is set accordingly
        """
        del self.sector.attrib['vocabulary']
        self.parser_201.iati_activities__iati_activity__sector(self.sector)
        sector = self.parser_201.get_model('ActivitySector')

        self.assertTrue(sector.vocabulary.code == "1")

    def test_sector_105(self):
        """
        Using the sectorvocabulary mappings
        """
        self.sector.attrib['vocabulary'] = 'DAC' # should map to 1
        self.parser_105.iati_activities__iati_activity__sector(self.sector)
        sector = self.parser_105.get_model('ActivitySector')

        self.assertTrue(sector.activity == self.activity)
        self.assertTrue(sector.sector.code == self.attrs['code'])
        self.assertTrue(sector.percentage == self.attrs['percentage'])
        self.assertTrue(sector.vocabulary.code == self.attrs['vocabulary'])

class CountryBudgetItemsTestCase(ParserSetupTestCase):
    """
    1.03: This is a new element, introduced in version 1.03 of the standard.
    """

    def setUp(self):
        self.iati_201 = copy_xml_tree(self.iati_201) # sample attributes on iati-activity xml

        self.attrs = {
            "vocabulary": "1", # IATI
        }

        self.country_budget_items = E('country_budget_items', **self.attrs)
        self.narrative = E('narrative', "Some description")

        self.test_country_budget_items = iati_factory.CountryBudgetItemFactory.build()

        self.activity = build_activity(version="2.01")
        self.parser_201.register_model('Activity', self.activity)
        self.parser_201.register_model('CountryBudgetItem', self.test_country_budget_items)
        self.parser_105.register_model('Activity', self.activity)
        self.parser_105.register_model('CountryBudgetItem', self.test_country_budget_items)

    def test_country_budget_items_201(self):
        """
        Along with its narrative(s)
        """
        self.parser_201.iati_activities__iati_activity__country_budget_items(self.country_budget_items)
        country_budget_item = self.parser_201.get_model('CountryBudgetItem')

        self.assertTrue(country_budget_item.activity == self.activity)
        self.assertTrue(country_budget_item.vocabulary.code == self.attrs['vocabulary'])

    def test_budget_item_201(self):
        """
        Along with its narrative(s)
        """
        budget_item = E('budget-item', code="1.1.1", percentage="50.21") # Executive - executive
        self.parser_201.iati_activities__iati_activity__country_budget_items__budget_item(budget_item)
        budget_item = self.parser_201.get_model('BudgetItem')

        self.assertTrue(budget_item.code.code == "1.1.1")
        self.assertTrue(budget_item.country_budget_item == self.test_country_budget_items)
        self.assertTrue(budget_item.percentage == "50.21")

    def test_budget_item_description_201(self):
        """
        Along with its narrative(s)
        """
        budget_item = iati_factory.BudgetItemFactory.build()
        self.parser_201.register_model('BudgetItem', budget_item)

        budget_item_description = E('description', code="1.1.1", percentage="50.21") # Executive - executive
        self.parser_201.iati_activities__iati_activity__country_budget_items__budget_item__description(budget_item_description)
        budget_item_description = self.parser_201.get_model('BudgetItemDescription')

        self.assertTrue(budget_item_description.budget_item == budget_item)

        self.parser_201.iati_activities__iati_activity__country_budget_items__budget_item__description__narrative(self.narrative)
        narrative = self.parser_201.get_model('BudgetItemDescriptionNarrative')
        self.assertTrue(narrative.related_object == budget_item_description)

    def test_budget_item_description_105(self):
        budget_item = iati_factory.BudgetItemFactory.build()
        self.parser_105.register_model('BudgetItem', budget_item)

        budget_item_description = E('description', "some text", code="1.1.1", percentage="50.21") # Executive - executive
        self.parser_105.iati_activities__iati_activity__country_budget_items__budget_item__description(budget_item_description)
        budget_item_description = self.parser_105.get_model('BudgetItemDescription')

        self.assertTrue(budget_item_description.budget_item == budget_item)

        narrative = self.parser_105.get_model('BudgetItemDescriptionNarrative')
        self.assertTrue(narrative.related_object == budget_item_description)

class PolicyMarkerTestCase(ParserSetupTestCase):
    """
    1.03: Where used, the @percentage attribute is now designated as a decimal value and no longer as a positive Integer
    """

    def setUp(self):
        self.iati_201 = copy_xml_tree(self.iati_201) # sample attributes on iati-activity xml

        self.attrs = {
            "code": "1", # Gender Equality
            "vocabulary": "1", # OECD-DAC CRS
            "significance": "1", # Significant objective
        }

        self.activity_policy_marker = E('policy-marker', **self.attrs)
        self.narrative = E('narrative', "Some description")

        self.activity = build_activity(version="2.01")
        self.parser_201.register_model('Activity', self.activity)
        self.parser_105.register_model('Activity', self.activity)

    def test_activity_policy_marker_201(self):
        """
        Along with its narrative(s)
        """
        self.parser_201.iati_activities__iati_activity__policy_marker(self.activity_policy_marker)
        activity_policy_marker = self.parser_201.get_model('ActivityPolicyMarker')

        self.assertTrue(activity_policy_marker.activity == self.activity)
        self.assertTrue(activity_policy_marker.code.code == self.attrs['code'])
        self.assertTrue(activity_policy_marker.significance.code == self.attrs['significance'])
        self.assertTrue(activity_policy_marker.vocabulary.code == self.attrs['vocabulary'])

        self.parser_201.iati_activities__iati_activity__policy_marker__narrative(self.narrative)
        narrative = self.parser_201.get_model('ActivityPolicyMarkerNarrative')
        self.assertTrue(narrative.related_object == activity_policy_marker)

    def test_activity_policy_marker_201_vocabulary_ommited(self):
        """
        An IATI code for the vocabulary to be used to define policy markers. 
        If omitted then the OECD DAC vocabulary is assumed.
        """
        attrs = self.attrs
        del attrs['vocabulary']
        activity_policy_marker = E('policy-marker', **attrs)
        self.parser_201.iati_activities__iati_activity__policy_marker(activity_policy_marker)
        activity_policy_marker = self.parser_201.get_model('ActivityPolicyMarker')
        self.assertTrue(activity_policy_marker.vocabulary.code == "1")

    def test_activity_policy_marker_105(self):
        """
        Should perform the (less than ideal) mapping from 105 Vocabulary to 201 PolicyMarkerVocabulary
        TODO: custom mappings
        see http://iatistandard.org/201/activity-standard/iati-activities/iati-activity/policy-marker/narrative/
        """
        self.activity_policy_marker.attrib['vocabulary'] = 'DAC'
        self.activity_policy_marker.text = 'Some description'

        self.parser_105.iati_activities__iati_activity__policy_marker(self.activity_policy_marker)
        activity_policy_marker = self.parser_105.get_model('ActivityPolicyMarker')

        self.assertTrue(activity_policy_marker.activity == self.activity)
        self.assertTrue(activity_policy_marker.code.code == self.attrs['code'])
        self.assertTrue(activity_policy_marker.significance.code == self.attrs['significance'])
        self.assertTrue(activity_policy_marker.vocabulary.code == self.attrs['vocabulary'])

        narrative = self.parser_105.get_model('ActivityPolicyMarkerNarrative')
        self.assertTrue(narrative.related_object == activity_policy_marker)

class BudgetTestCase(ParserSetupTestCase):
    """
    No changes
    """

    def setUp(self):
        self.iati_201 = copy_xml_tree(self.iati_201) # sample attributes on iati-activity xml

        self.attrs = {
            "type": "1", # Original
        }

        self.budget = E('budget', **self.attrs)
        self.narrative = E('narrative', "Some description")

        self.activity = build_activity(version="2.01")
        self.parser_201.register_model('Activity', self.activity)
        self.parser_105.register_model('Activity', self.activity)

    def test_budget_201(self):
        """
        """
        self.parser_201.iati_activities__iati_activity__budget(self.budget)
        budget = self.parser_201.get_model('Budget')

        self.assertTrue(budget.activity == self.activity)
        self.assertTrue(budget.type.code == self.attrs['type'])

    def test_budget_period_start_201(self):
        """
        """
        attrs = {
            "iso-date": datetime.datetime.now().isoformat(' ')
        }

        period_start = E('period-start', **attrs) 
        self.parser_201.iati_activities__iati_activity__budget__period_start(period_start)
        budget = self.parser_201.get_model('Budget')

        self.assertTrue(str(budget.period_start) == attrs['iso-date'])

    def test_budget_period_end_201(self):
        """
        """
        attrs = {
            "iso-date": datetime.datetime.now().isoformat(' ')
        }

        period_end = E('period-end', **attrs) 
        self.parser_201.iati_activities__iati_activity__budget__period_end(period_end)
        budget = self.parser_201.get_model('Budget')

        self.assertTrue(str(budget.period_end) == attrs['iso-date'])

    def test_budget_value_201(self):
        """
        All attributes available
        """
        attrs = {
            "currency": "EUR",
            "value-date": datetime.datetime.now().isoformat(' ')
        }
        text = "2000.2"

        xdr_value = 200
        currency_from_to = convert.currency_from_to
        convert.currency_from_to = MagicMock(return_value=xdr_value)

        value = E('value', text, **attrs) 
        self.parser_201.iati_activities__iati_activity__budget__value(value)
        budget = self.parser_201.get_model('Budget')
        budget.save()

        self.assertTrue(budget.value == Decimal('2000.2'))
        self.assertTrue(str(budget.value_date) == attrs['value-date'])
        self.assertTrue(budget.currency.code == attrs['currency'])

        self.assertTrue(budget.xdr_value == xdr_value)
        self.assertTrue(budget.usd_value == xdr_value)
        self.assertTrue(budget.eur_value == xdr_value)
        self.assertTrue(budget.gbp_value == xdr_value)
        self.assertTrue(budget.jpy_value == xdr_value)
        self.assertTrue(budget.cad_value == xdr_value)

        convert.currency_from_to = currency_from_to

    def test_budget_no_value_date_should_not_parse_201(self):
        """
        When the value-date is not set, the budget should not be parsed
        """
        attrs = {
            "currency": "EUR",
        }
        text = "2000.2"

        value = E('value', text, **attrs)

        with self.assertRaises(Exception):
            self.parser_201.iati_activities__iati_activity__budget__value(value)

    def test_budget_wrong_value_should_not_parse_201(self):
        """
        When the value field is invalid, only store it as a string for future reference
        """
        attrs = {
            "currency": "EUR",
            "value-date": datetime.datetime.now().isoformat(' ')
        }
        text = "1.000.000.000,2"

        value = E('value', text, **attrs)

        with self.assertRaises(ValidationError):
            self.parser_201.iati_activities__iati_activity__budget__value(value)


class PlannedDisbursementTestCase(ParserSetupTestCase):
    """
    2.01: The attribute @last-updated was removed.
    2.01: The attribute @type was added.
    1.05: A description was added to this element # ?
    """

    def setUp(self):
        self.iati_201 = copy_xml_tree(self.iati_201) # sample attributes on iati-activity xml

        self.attrs = {
            "type": "1", # Original
        }

        self.planned_disbursement = E('planned-disbursement', **self.attrs)
        self.narrative = E('narrative', "Some description")

        self.activity = build_activity(version="2.01")
        self.parser_201.register_model('Activity', self.activity)
        self.parser_105.register_model('Activity', self.activity)

    def test_planned_disbursement_201(self):
        """
        """
        self.parser_201.iati_activities__iati_activity__planned_disbursement(self.planned_disbursement)
        planned_disbursement = self.parser_201.get_model('PlannedDisbursement')

        self.assertTrue(planned_disbursement.activity == self.activity)
        self.assertTrue(planned_disbursement.type.code == self.attrs['type'])

    def test_planned_disbursement_period_start_201(self):
        """
        """
        attrs = {
            "iso-date": datetime.datetime.now().isoformat(' ')
        }

        period_start = E('period-start', **attrs) 
        self.parser_201.iati_activities__iati_activity__planned_disbursement__period_start(period_start)
        planned_disbursement = self.parser_201.get_model('PlannedDisbursement')

        self.assertTrue(str(planned_disbursement.period_start) == attrs['iso-date'])

    def test_planned_disbursement_period_end_201(self):
        """
        """
        attrs = {
            "iso-date": datetime.datetime.now().isoformat(' ')
        }

        period_end = E('period-end', **attrs) 
        self.parser_201.iati_activities__iati_activity__planned_disbursement__period_end(period_end)
        planned_disbursement = self.parser_201.get_model('PlannedDisbursement')

        self.assertTrue(str(planned_disbursement.period_end) == attrs['iso-date'])

    def test_planned_disbursement_value_201(self):
        """
        All attributes available
        """
        attrs = {
            "currency": "EUR",
            "value-date": datetime.datetime.now().isoformat(' ')
        }
        text = "2000.2"

        value = E('value', text, **attrs) 
        self.parser_201.iati_activities__iati_activity__planned_disbursement__value(value)
        planned_disbursement = self.parser_201.get_model('PlannedDisbursement')
        planned_disbursement.save()

        self.assertTrue(planned_disbursement.value == Decimal('2000.2'))
        self.assertTrue(str(planned_disbursement.value_date) == attrs['value-date'])
        self.assertTrue(planned_disbursement.currency.code == attrs['currency'])

    def test_planned_disbursement_no_value_date_should_not_parse_201(self):
        """
        When the value-date is not set, the budget should not be parsed
        """
        attrs = {
            "currency": "EUR",
        }
        text = "2000.2"

        value = E('value', text, **attrs)

        with self.assertRaises(Exception):
            self.parser_201.iati_activities__iati_activity__planned_disbursement__value(value)


class TransactionTestCase(ParserSetupTestCase):
    """
    2.01: The attribute @last-updated was removed.
    2.01: The attribute @type was added.
    1.05: A description was added to this element # ?
    """

    def setUp(self):
        self.iati_201 = copy_xml_tree(self.iati_201) # sample attributes on iati-activity xml

        self.attrs = {
            "ref": "12345", # Internal reference
        }

        self.transaction = E('transaction', **self.attrs)
        self.narrative = E('narrative', "Some description")

        self.activity = build_activity(version="2.01")
        self.parser_201.register_model('Activity', self.activity)
        self.parser_105.register_model('Activity', self.activity)

        self.test_transaction = transaction_factory.TransactionFactory.build()
        self.parser_201.register_model('Transaction', self.test_transaction)
        self.parser_105.register_model('Transaction', self.test_transaction)

    def test_transaction_201(self):
        self.parser_201.iati_activities__iati_activity__transaction(self.transaction)
        transaction = self.parser_201.get_model('Transaction')

        self.assertTrue(transaction.activity == self.activity)
        self.assertTrue(transaction.ref == self.attrs['ref'])

    def test_transaction_transaction_type_105(self):
        transaction_type = E('transaction-type', code="1") # Incoming funds
        self.parser_105.iati_activities__iati_activity__transaction__transaction_type(transaction_type)
        transaction = self.parser_105.get_model('Transaction')

        self.assertTrue(transaction.transaction_type.code == "1")

    def test_transaction_transaction_type_105(self):
        transaction_type = E('transaction-type', code="IF") # Incoming funds
        self.parser_105.iati_activities__iati_activity__transaction__transaction_type(transaction_type)
        transaction = self.parser_105.get_model('Transaction')

        self.assertTrue(transaction.transaction_type.code == "1")

    def test_transaction_transaction_date_201(self):
        attrs = {
            "iso-date": datetime.datetime.now().isoformat(' ')
        }
        transaction_date = E('transaction-date', **attrs)
        self.parser_201.iati_activities__iati_activity__transaction__transaction_date(transaction_date)
        transaction = self.parser_201.get_model('Transaction')

        self.assertTrue(str(transaction.transaction_date) == attrs['iso-date'])

    def test_transaction_value_201(self):
        """
        All attributes available
        """
        attrs = {
            "currency": "EUR",
            "value-date": datetime.datetime.now().isoformat(' ')
        }

        value_text = "2000.2"
        xdr_value = 300

        value = E('value', value_text, **attrs)

        # mock xdr canculation
        currency_from_to = convert.currency_from_to
        convert.currency_from_to = MagicMock(return_value=xdr_value)

        self.parser_201.iati_activities__iati_activity__transaction__value(value)
        transaction = self.parser_201.get_model('Transaction')
        transaction.save()

        self.assertTrue(transaction.value == Decimal(value_text))
        self.assertTrue(str(transaction.value_date) == attrs['value-date'])
        self.assertTrue(transaction.currency.code == attrs['currency'])

        self.assertTrue(transaction.xdr_value == xdr_value)
        self.assertTrue(transaction.usd_value == xdr_value)
        self.assertTrue(transaction.eur_value == xdr_value)
        self.assertTrue(transaction.gbp_value == xdr_value)
        self.assertTrue(transaction.jpy_value == xdr_value)
        self.assertTrue(transaction.cad_value == xdr_value)

        convert.currency_from_to = currency_from_to

    def test_transaction_no_value_date_should_not_parse_201(self):
        """
        When the value-date is not set, the transaction should not be parsed
        """
        attrs = {
            "currency": "EUR",
        }
        text = "2000.2"

        value = E('value', text, **attrs)

        with self.assertRaises(Exception):
            self.parser_201.iati_activities__iati_activity__transaction__value(value)

    def test_transaction_description_201(self):
        description = E('description')
        self.parser_201.iati_activities__iati_activity__transaction__description(description)
        transaction_description = self.parser_201.get_model('TransactionDescription')

        self.assertTrue(transaction_description.transaction == self.test_transaction)

        self.parser_201.iati_activities__iati_activity__transaction__description__narrative(self.narrative)
        narrative = self.parser_201.get_model('TransactionDescriptionNarrative')
        self.assertTrue(narrative.related_object == transaction_description)

    def test_transaction_description_105(self):
        description = E('description', 'some text')
        self.parser_105.iati_activities__iati_activity__transaction__description(description)
        transaction_description = self.parser_105.get_model('TransactionDescription')

        self.assertTrue(transaction_description.transaction == self.test_transaction)

        narrative = self.parser_105.get_model('TransactionDescriptionNarrative')
        self.assertTrue(narrative.related_object == transaction_description)

    def test_transaction_disbursement_channel_201(self):
        """
        """

        disbursement_channel = E('disbursement_channel', code="1") 
        self.parser_201.iati_activities__iati_activity__transaction__disbursement_channel(disbursement_channel)
        transaction = self.parser_201.get_model('Transaction')

        self.assertTrue(transaction.disbursement_channel.code == "1")

    def test_transaction_sector_201(self):
        """
        """
        attrs = {
            "code": "11110", # Education Policy and administrative management
            "vocabulary": "1", # OECD-DAC-5
        }

        sector = E('sector', **attrs) 
        self.parser_201.iati_activities__iati_activity__transaction__sector(sector)
        transaction_sector = self.parser_201.get_model('TransactionSector')

        self.assertTrue(transaction_sector.transaction == self.test_transaction)
        self.assertTrue(transaction_sector.sector.code == attrs['code'])
        self.assertTrue(transaction_sector.vocabulary.code == attrs['vocabulary'])
        self.assertTrue(transaction_sector.percentage == 100)

    def test_transaction_recipient_country_201(self):
        """
        """
        attrs = {
            "code": "AF",
            "percentage": "50.5",
        }

        recipient_country = E('recipient_country', **attrs) 
        self.parser_201.iati_activities__iati_activity__transaction__recipient_country(recipient_country)
        transaction_recipient_country = self.parser_201.get_model('TransactionRecipientCountry')

        self.assertTrue(transaction_recipient_country.transaction == self.test_transaction)
        self.assertTrue(transaction_recipient_country.country.code == attrs['code'])
        self.assertTrue(transaction_recipient_country.percentage == 100)

    def test_transaction_recipient_region_201(self):
        """

        """
        attrs = {
            "code": "89", # Europe, regional
            "vocabulary": "1", # OECD-DAC
            "percentage": "50.5",
        }

        recipient_region = E('recipient_region', **attrs) 
        self.parser_201.iati_activities__iati_activity__transaction__recipient_region(recipient_region)
        transaction_recipient_region = self.parser_201.get_model('TransactionRecipientRegion')

        self.assertTrue(transaction_recipient_region.transaction == self.test_transaction)
        self.assertTrue(transaction_recipient_region.region.code == attrs['code'])
        self.assertTrue(transaction_recipient_region.vocabulary.code == attrs['vocabulary'])
        self.assertTrue(transaction_recipient_region.percentage == 100)

    def test_transaction_flow_type_201(self):
        """
        """

        flow_type = E('flow-type', code="10") # ODA
        self.parser_201.iati_activities__iati_activity__transaction__flow_type(flow_type)
        transaction = self.parser_201.get_model('Transaction')

        self.assertTrue(transaction.flow_type.code == "10")

    @skip('NotImplemented')
    def test_transaction_flow_type_inherits_activity_201(self):
        """
        must inherit from the corresponding activity field
        """


    def test_transaction_finance_type_activity_201(self):
        """
        """

        finance_type = E('finance-type', code="110") # Aid grant excl.
        self.parser_201.iati_activities__iati_activity__transaction__finance_type(finance_type)
        transaction = self.parser_201.get_model('Transaction')

        self.assertTrue(transaction.finance_type.code == "110")

    @skip('NotImplemented')
    def test_transaction_finance_type_inherits_activity_201(self):
        """
        must inherit from the corresponding activity field
        """
        raise NotImplementedError()

    def test_transaction_aid_type_activity_201(self):
        aid_type = E('aid-type', code="A01") # General budget support
        self.parser_201.iati_activities__iati_activity__transaction__aid_type(aid_type)
        transaction = self.parser_201.get_model('Transaction')

        self.assertTrue(transaction.aid_type.code == "A01")

    @skip('NotImplemented')
    def test_transaction_aid_type_inherits_activity_201(self):
        """
        must inherit from the corresponding activity field
        """
        raise NotImplementedError()

    def test_transaction_tied_status_activity_201(self):
        """
        """
        tied_status = E('tied-status', code="4") # Tied
        self.parser_201.iati_activities__iati_activity__transaction__tied_status(tied_status)
        transaction = self.parser_201.get_model('Transaction')

        self.assertTrue(transaction.tied_status.code == "4")

    @skip('NotImplemented')
    def test_transaction_tied_status_inherits_activity_201(self):
        """
        must inherit from the corresponding activity field
        """

        raise NotImplementedError()


class ProviderOrganisationTestCase(ParserSetupTestCase):
    def setUp(self):
        self.iati_201 = copy_xml_tree(self.iati_201)

        self.attrs = {
            "ref": "GB-COH-03580586",
            "provider-activity-id": 'no constraints on this field',
        }

        self.provider_org = E('provider-org', **self.attrs)

        self.narrative = E('narrative', "random text")

        self.activity = build_activity(version="2.01")
        self.parser_201.register_model('Activity', self.activity)
        self.parser_105.register_model('Activity', self.activity)

        self.test_transaction = transaction_factory.TransactionFactory.build()
        self.parser_201.register_model('Transaction', self.test_transaction)
        self.parser_105.register_model('Transaction', self.test_transaction)

    def test_provider_organisation_not_parsed_yet_201(self):
        """
        Check element is parsed correctly, excluding narratives when organisation is not in the organisation API. This results in the organisation field being empty
        """

        self.parser_201.iati_activities__iati_activity__transaction__provider_org(self.provider_org)
        provider_organisation = self.parser_201.get_model('TransactionProvider')

        self.assertTrue(provider_organisation.ref == self.attrs['ref'])
        self.assertTrue(provider_organisation.organisation == None)
        self.assertTrue(provider_organisation.transaction == self.test_transaction)
        # self.assertTrue(provider_organisation.provider_activity_id == self.attrs['provider-activity-id'])

        self.parser_201.iati_activities__iati_activity__transaction__provider_org__narrative(self.narrative)
        narrative = self.parser_201.get_model('TransactionProviderNarrative')
        self.assertTrue(narrative.related_object == provider_organisation)
        self.assertTrue(provider_organisation.primary_name == 'random text')

        # TODO: refactor so this isnt nescessary
        provider_organisation = self.parser_201.pop_model('TransactionProvider')

    
    @skip('NotImplemented')
    def test_provider_organisation_duplicate(self):
        """
        Duplicates are not allowed
        """
        self.parser_201.iati_activities__iati_activity__transaction__provider_org(self.provider_org)

        with self.assertRaises(Exception):
            self.parser_201.iati_activities__iati_activity__transaction__provider_org(self.provider_org)

        # TODO: refactor so this isnt nescessary
        provider_organisation = self.parser_201.pop_model('TransactionProvider')

    def test_provider_organisation_narrative_105(self):
        """
        Check element is parsed correctly, excluding narratives when organisation is not in the organisation API. This results in the organisation field being empty
        """
        self.provider_org.text = "random text"
        self.parser_105.iati_activities__iati_activity__transaction__provider_org(self.provider_org)
        provider_organisation = self.parser_105.get_model('TransactionProvider')

        self.test_transaction = transaction_factory.TransactionFactory.build()
        self.parser_201.register_model('Transaction', self.test_transaction)
        narrative = self.parser_105.get_model('TransactionProviderNarrative')
        self.assertTrue(narrative.related_object == provider_organisation)
        self.assertTrue(provider_organisation.primary_name == 'random text')

        # TODO: refactor so this isnt nescessary
        provider_organisation = self.parser_201.pop_model('TransactionProvider')

    @skip('NotImplemented')
    def test_provider_organisation_provider_activity_exists(self):
        raise NotImplementedError()

    @skip('NotImplemented')
    def test_provider_organisation_provider_activity_has_related(self):
        raise NotImplementedError()


class ReceiverOrganisationTestCase(ParserSetupTestCase):
    def setUp(self):
        self.attrs = {
            "ref": "GB-COH-03580586",
            "receiver-activity-id": 'no constraints on this field',
        }

        self.receiver_org = E('receiver-org', **self.attrs)

        self.iati_201 = copy_xml_tree(self.iati_201)

        self.narrative = E('narrative', "random text")

        self.activity = build_activity(version="2.01")
        self.parser_201.register_model('Activity', self.activity)
        self.parser_105.register_model('Activity', self.activity)

        self.test_transaction = transaction_factory.TransactionFactory.build()
        self.parser_201.register_model('Transaction', self.test_transaction)
        self.parser_105.register_model('Transaction', self.test_transaction)

    def test_receiver_organisation_not_parsed_yet_201(self):
        """
        Check element is parsed correctly, excluding narratives when organisation is not in the organisation API. This results in the organisation field being empty
        """
        self.parser_201.iati_activities__iati_activity__transaction__receiver_org(self.receiver_org)
        receiver_organisation = self.parser_201.get_model('TransactionReceiver')

        self.assertTrue(receiver_organisation.ref == self.attrs['ref'])
        self.assertTrue(receiver_organisation.organisation == None)
        self.assertTrue(receiver_organisation.receiver_activity_id == None)
        self.assertTrue(receiver_organisation.transaction == self.test_transaction)

        self.parser_201.iati_activities__iati_activity__transaction__receiver_org__narrative(self.narrative)
        narrative = self.parser_201.get_model('TransactionReceiverNarrative')
        self.assertTrue(narrative.related_object == receiver_organisation)
        self.assertTrue(receiver_organisation.primary_name == 'random text')

        # TODO: refactor so this isnt nescessary
        receiver_organisation = self.parser_201.pop_model('TransactionReceiver')

    @skip('NotImplemented')
    def test_receiver_organisation_duplicate(self):
        """
        Duplicates are not allowed
        """
        self.parser_201.iati_activities__iati_activity__transaction__receiver_org(self.receiver_org)

        with self.assertRaises(Exception):
            self.parser_201.iati_activities__iati_activity__transaction__receiver_org(self.receiver_org)

        # TODO: refactor so this isnt nescessary
        receiver_organisation = self.parser_201.pop_model('TransactionReceiver')

    @skip('NotImplemented')
    def test_receiver_organisation_receiver_activity_exists(self):
        raise NotImplementedError()

    @skip('NotImplemented')
    def test_receiver_organisation_receiver_activity_has_related(self):
        raise NotImplementedError()

    def test_receiver_organisation_narrative_105(self):
        """
        Check element is parsed correctly, excluding narratives when organisation is not in the organisation API. This results in the organisation field being empty
        """
        self.receiver_org.text = 'random text'
        self.parser_105.iati_activities__iati_activity__transaction__receiver_org(self.receiver_org)
        receiver_organisation = self.parser_105.get_model('TransactionReceiver')

        narrative = self.parser_105.get_model('TransactionReceiverNarrative')
        self.assertTrue(narrative.related_object == receiver_organisation)
        self.assertTrue(receiver_organisation.primary_name == 'random text')

        # TODO: refactor so this isnt nescessary
        receiver_organisation = self.parser_105.pop_model('TransactionReceiver')

class DocumentLinkTestCase(ParserSetupTestCase):
    """
    1.02: Removed @language attribute from, and introduced an new language child element to, the document-link element.
    """

    def setUp(self):
        self.iati_201 = copy_xml_tree(self.iati_201) # sample attributes on iati-activity xml

        self.attrs = {
            "url": "http://zimmermanzimmerman.nl/",
            "format": "text/html",
        }

        self.document_link = E('document-link', **self.attrs)
        self.narrative = E('narrative', "Some description")

        self.activity = build_activity(version="2.01")
        self.parser_201.register_model('Activity', self.activity)
        self.parser_105.register_model('Activity', self.activity)

        self.test_document_link = iati_factory.DocumentLinkFactory.build()
        self.parser_201.register_model('DocumentLink', self.test_document_link)
        self.parser_105.register_model('DocumentLink', self.test_document_link)

    def test_document_link_201(self):
        """
        """
        self.parser_201.iati_activities__iati_activity__document_link(self.document_link)
        document_link = self.parser_201.get_model('DocumentLink')

        self.assertTrue(document_link.activity == self.activity)
        self.assertTrue(document_link.url == self.attrs['url'])
        self.assertTrue(document_link.file_format.code == self.attrs['format'])

    def test_document_link_title_201(self):
        """
        """

        title = E('title') 
        self.parser_201.iati_activities__iati_activity__document_link__title(title)
        document_link_title = self.parser_201.get_model('DocumentLinkTitle')

        self.assertTrue(document_link_title.document_link == self.test_document_link)

        self.parser_201.iati_activities__iati_activity__document_link__title__narrative(self.narrative)
        narrative = self.parser_201.get_model('DocumentLinkTitleNarrative')
        self.assertTrue(narrative.related_object == document_link_title)

    def test_document_link_category_201(self):
        """
        """

        category = E('category', code="A04") # conditions
        self.parser_201.iati_activities__iati_activity__document_link__category(category)
        document_link_category = self.parser_201.get_model('DocumentLinkCategory')

        self.assertTrue(document_link_category.document_link == self.test_document_link)
        self.assertTrue(document_link_category.category.code == "A04")

    def test_document_link_language_201(self):
        """
        """

        language = E('language', code="en") # english
        self.parser_201.iati_activities__iati_activity__document_link__language(language)
        document_link_language = self.parser_201.get_model('DocumentLinkLanguage')

        self.assertTrue(document_link_language.document_link == self.test_document_link)
        self.assertTrue(document_link_language.language.code == "en")

class RelatedActivityTestCase(ParserSetupTestCase):
    """
    2.01: Freetext is no longer allowed within this element.
    """

    def setUp(self):
        self.iati_201 = copy_xml_tree(self.iati_201) # sample attributes on iati-activity xml

        self.attrs = {
            "ref": "IATI-0002",
            "type": "1", # parent
        }

        self.related_activity = E('related-activity', **self.attrs)
        self.narrative = E('narrative', "Some description")

        self.activity = build_activity(version="2.01")
        self.parser_201.register_model('Activity', self.activity)
        self.parser_105.register_model('Activity', self.activity)

    def test_related_activity_no_related_201(self):
        """
        related activity does not exist (just save ref)
        """
        self.parser_201.iati_activities__iati_activity__related_activity(self.related_activity)
        related_activity = self.parser_201.get_model('RelatedActivity')

        self.assertTrue(related_activity.current_activity == self.activity)
        self.assertTrue(related_activity.ref_activity == None)
        self.assertTrue(related_activity.ref == self.attrs['ref'])
        self.assertTrue(related_activity.type.code == self.attrs['type'])

    def test_related_activity_has_related_201(self):
        """
        related activity does exist and should be saved accordingly
        """
        test_related_activity = build_activity(version="2.01", iati_identifier="IATI-0002")
        test_related_activity.save()

        self.parser_201.iati_activities__iati_activity__related_activity(self.related_activity)
        related_activity = self.parser_201.get_model('RelatedActivity')

        self.assertTrue(related_activity.current_activity == self.activity)
        self.assertTrue(related_activity.ref_activity == test_related_activity)
        self.assertTrue(related_activity.ref == self.attrs['ref'])
        self.assertTrue(related_activity.type.code == self.attrs['type'])

    def test_related_activity_update_existing_201(self):
        """
        should update existing activities that have related-activity fields pointing to this activity
        this happens post save through def set_related_activities
        """

        self.activity.save()
        test_related_activity = iati_factory.RelatedActivityFactory.build(ref="IATI-0001", ref_activity=None)
        test_related_activity.save()
        self.assertTrue(test_related_activity.ref_activity == None)

        from iati.parser import post_save
        post_save.set_related_activities(self.activity)

        test_related_activity.refresh_from_db()

        self.assertTrue(test_related_activity.ref_activity == self.activity)


class ResultTestCase(ParserSetupTestCase):
    """
    2.01: Freetext is no longer allowed within this element.
    """

    def setUp(self):
        self.iati_201 = copy_xml_tree(self.iati_201) # sample attributes on iati-activity xml

        self.attrs = {
            "type": "1", # output
            "aggregation-status": "1", # suitable for aggregation
        }

        self.result = E('result', **self.attrs)
        self.narrative = E('narrative', "Some description")

        self.activity = build_activity(version="2.01")
        self.test_result = iati_factory.ResultFactory.build()
        self.test_result_indicator = iati_factory.ResultIndicatorFactory.build()

        self.parser_201.register_model('Activity', self.activity)
        self.parser_201.register_model('Result', self.test_result)
        self.parser_201.register_model('ResultIndicator', self.test_result_indicator)
        self.parser_105.register_model('Activity', self.activity)
        self.parser_105.register_model('Result', self.test_result)
        self.parser_105.register_model('ResultIndicator', self.test_result_indicator)

    def test_result(self):
        """
        related activity does not exist (just save ref)
        """
        self.parser_201.iati_activities__iati_activity__result(self.result)
        result = self.parser_201.get_model('Result')

        self.assertEquals(result.activity, self.activity)
        self.assertEquals(result.type.code, self.attrs['type'])
        self.assertEquals(result.aggregation_status, bool(int(self.attrs['aggregation-status'])))

    def test_result_title_201(self):
        """
        test for result_title + accompanying narrative
        """

        title = E('title') 
        self.parser_201.iati_activities__iati_activity__result__title(title)
        result_title = self.parser_201.get_model('ResultTitle')

        self.assertEquals(result_title.result, self.test_result)

        self.parser_201.iati_activities__iati_activity__result__title__narrative(self.narrative)
        narrative = self.parser_201.get_model('ResultTitleNarrative')
        self.assertEquals(narrative.related_object, result_title)

    def test_result_title_105(self):
        """
        test for result_title + accompanying narrative
        """
        title = E('title', 'some title') 
        self.parser_105.iati_activities__iati_activity__result__title(title)

        result_title = self.parser_105.get_model('ResultTitle')
        self.assertEquals(result_title.result, self.test_result)

        narrative = self.parser_105.get_model('ResultTitleNarrative')
        self.assertEquals(narrative.related_object, result_title)

    def test_result_title_105_duplicates(self):
        """
        Check that adding two result title elements in 105 gets added as narratives on the same result_title object
        """
        title1 = E('title', 'some title') 
        title2 = E('title', 'some title') 

        self.parser_105.iati_activities__iati_activity__result__title(title1)
        self.parser_105.iati_activities__iati_activity__result__title(title2)

        result_title = self.parser_105.get_model('ResultTitle')
        self.assertEquals(result_title.result, self.test_result)

        narrative1 = self.parser_105.get_model('ResultTitleNarrative')
        narrative2 = self.parser_105.get_model('ResultTitleNarrative')
        self.assertEquals(narrative1.related_object, result_title)
        self.assertEquals(narrative2.related_object, result_title)

    def test_result_description_201(self):
        """
        test for result_description + accompanying narrative
        """

        description = E('description') 
        self.parser_201.iati_activities__iati_activity__result__description(description)
        result_description = self.parser_201.get_model('ResultDescription')

        self.assertEquals(result_description.result, self.test_result)

        self.parser_201.iati_activities__iati_activity__result__description__narrative(self.narrative)
        narrative = self.parser_201.get_model('ResultDescriptionNarrative')
        self.assertEquals(narrative.related_object, result_description)

    def test_result_description_105(self):
        """
        test for result_description + accompanying narrative
        """
        result_description = E('description', 'some description') 
        self.parser_105.iati_activities__iati_activity__result__description(result_description)

        result_description = self.parser_105.get_model('ResultDescription')
        self.assertEquals(result_description.result, self.test_result)

        narrative = self.parser_105.get_model('ResultDescriptionNarrative')
        self.assertEquals(narrative.related_object, result_description)

    def test_result_description_105_duplicates(self):
        """
        Check that adding two result description elements in 105 gets added as narratives on the same result_description object
        """
        description1 = E('description', 'some description') 
        description2 = E('description', 'some description') 

        self.parser_105.iati_activities__iati_activity__result__description(description1)
        self.parser_105.iati_activities__iati_activity__result__description(description2)

        result_description = self.parser_105.get_model('ResultDescription')
        self.assertEquals(result_description.result, self.test_result)

        narrative1 = self.parser_105.get_model('ResultDescriptionNarrative')
        narrative2 = self.parser_105.get_model('ResultDescriptionNarrative')
        self.assertEquals(narrative1.related_object, result_description)
        self.assertEquals(narrative2.related_object, result_description)

    def test_result_indicator_201(self):
        """
        test for result_indicator + accompanying narrative
        """
        attrs = {
            'measure': '1', # unit
            'ascending': '1' # ascending           
        }
        result_indicator = E('indicator', **attrs) 
        self.parser_201.iati_activities__iati_activity__result__indicator(result_indicator)

        result_indicator = self.parser_201.get_model('ResultIndicator')
        self.assertEquals(result_indicator.result, self.test_result)
        self.assertEquals(result_indicator.measure.code, attrs['measure'])
        self.assertEquals(result_indicator.ascending, bool(int(attrs['ascending'])))


    def test_result_indicator_title_201(self):
        """
        test for result_indicator_title + accompanying narrative
        """

        indicator_title = E('indicator-title') 
        self.parser_201.iati_activities__iati_activity__result__indicator__title(indicator_title)
        result_indicator_title = self.parser_201.get_model('ResultIndicatorTitle')

        self.assertEquals(result_indicator_title.result_indicator, self.test_result_indicator)

        self.parser_201.iati_activities__iati_activity__result__indicator__title__narrative(self.narrative)
        narrative = self.parser_201.get_model('ResultIndicatorTitleNarrative')
        self.assertEquals(narrative.related_object, result_indicator_title)

    def test_result_indicator_title_105(self):
        """
        """

        result_indicator_title = E('indicator-title', 'some indicator_title') 
        self.parser_105.iati_activities__iati_activity__result__indicator__title(result_indicator_title)

        result_indicator_title = self.parser_105.get_model('ResultIndicatorTitle')
        self.assertEquals(result_indicator_title.result_indicator, self.test_result_indicator)

        narrative = self.parser_105.get_model('ResultIndicatorTitleNarrative')
        self.assertEquals(narrative.related_object, result_indicator_title)

    def test_result_indicator_description_201(self):
        """
        test for result_indicator_description + accompanying narrative
        """

        indicator_description = E('indicator-description') 
        self.parser_201.iati_activities__iati_activity__result__indicator__description(indicator_description)
        result_indicator_description = self.parser_201.get_model('ResultIndicatorDescription')

        self.assertEquals(result_indicator_description.result_indicator, self.test_result_indicator)

        self.parser_201.iati_activities__iati_activity__result__indicator__description__narrative(self.narrative)
        narrative = self.parser_201.get_model('ResultIndicatorDescriptionNarrative')
        self.assertEquals(narrative.related_object, result_indicator_description)

    def test_result_indicator_description_105(self):
        """
        """

        result_indicator_description = E('indicator-description', 'some indicator_description') 
        self.parser_105.iati_activities__iati_activity__result__indicator__description(result_indicator_description)

        result_indicator_description = self.parser_105.get_model('ResultIndicatorDescription')
        self.assertEquals(result_indicator_description.result_indicator, self.test_result_indicator)

        narrative = self.parser_105.get_model('ResultIndicatorDescriptionNarrative')
        self.assertEquals(narrative.related_object, result_indicator_description)

    def test_result_indicator_baseline(self):
        """
        test for result_indicator_baseline + accompanying narrative
        """
        attrs = {
            'year': '1992',
            'value': '100'
        }
        result_indicator_baseline = E('indicator-baseline', **attrs) 
        self.parser_201.iati_activities__iati_activity__result__indicator__baseline(result_indicator_baseline)

        result_indicator = self.parser_201.get_model('ResultIndicator')
        self.assertEquals(result_indicator.baseline_year, int(attrs['year']))
        self.assertEquals(result_indicator.baseline_value, Decimal(attrs['value']))

    def test_result_indicator_baseline_comment_201(self):
        """
        test for result_indicator_baseline_comment + accompanying narrative
        """

        test_target_comment = iati_factory.ResultIndicatorFactory.build()
        self.parser_201.register_model('ResultIndicator', test_target_comment)

        result_indicator_baseline_comment = E('comment') 
        self.parser_201.iati_activities__iati_activity__result__indicator__baseline__comment(result_indicator_baseline_comment)

        result_indicator_baseline_comment = self.parser_201.get_model('ResultIndicatorBaselineComment')
        self.assertEquals(result_indicator_baseline_comment.result_indicator, test_target_comment)

        self.parser_201.iati_activities__iati_activity__result__indicator__baseline__comment__narrative(self.narrative)
        narrative = self.parser_201.get_model('ResultIndicatorBaselineCommentNarrative')
        self.assertEquals(narrative.related_object, result_indicator_baseline_comment)

    def test_result_indicator_baseline_comment_105(self):
        """
        test for result_indicator_baseline_comment + accompanying narrative
        """

        test_target_comment = iati_factory.ResultIndicatorFactory.build()
        self.parser_105.register_model('ResultIndicator', test_target_comment)

        result_indicator_baseline_comment = E('comment', 'arie bombarie') 
        self.parser_105.iati_activities__iati_activity__result__indicator__baseline__comment(result_indicator_baseline_comment)

        result_indicator_baseline_comment = self.parser_105.get_model('ResultIndicatorBaselineComment')
        self.assertEquals(result_indicator_baseline_comment.result_indicator, test_target_comment)

        narrative = self.parser_105.get_model('ResultIndicatorBaselineCommentNarrative')
        self.assertEquals(narrative.related_object, result_indicator_baseline_comment)

    def test_result_indicator_period(self):
        """
        test for result_indicator_period + accompanying narrative
        """
        test_target_comment = iati_factory.ResultIndicatorFactory.build()
        self.parser_105.register_model('ResultIndicator', test_target_comment)

        result_indicator_period = E('period') 
        self.parser_201.iati_activities__iati_activity__result__indicator__period(result_indicator_period)

        result_period = self.parser_201.get_model('ResultIndicatorPeriod')
        result_period.result_indicator = test_target_comment

    def test_result_indicator_period_period_start(self):
        """
        test for result_period_start + accompanying narrative
        """
        test_period = iati_factory.ResultIndicatorPeriodFactory.build()
        self.parser_105.register_model('ResultIndicatorPeriod', test_period)

        attrs = {
            'iso-date': datetime.datetime.now().isoformat(' ')
        }

        result_period_start = E('period-start', **attrs) 
        self.parser_201.iati_activities__iati_activity__result__indicator__period__period_start(result_period_start)

        result_period = self.parser_201.get_model('ResultIndicatorPeriod')
        self.assertEquals(str(result_period.period_start), attrs['iso-date'])

    def test_result_indicator_period_period_end(self):
        """
        test for result_period_end + accompanying narrative
        """
        test_period = iati_factory.ResultIndicatorPeriodFactory.build()
        self.parser_105.register_model('ResultIndicatorPeriod', test_period)

        attrs = {
            'iso-date': datetime.datetime.now().isoformat(' ')
        }

        result_period_end = E('period-end', **attrs) 
        self.parser_201.iati_activities__iati_activity__result__indicator__period__period_end(result_period_end)

        result_period = self.parser_201.get_model('ResultIndicatorPeriod')
        self.assertEquals(str(result_period.period_end), attrs['iso-date'])

    def test_result_indicator_period_target(self):
        """
        test for result_indicator_period_target + accompanying narrative
        """

        attrs = {
            'value': '100'
        }

        result_indicator_period_target = E('target', **attrs) 
        self.parser_201.iati_activities__iati_activity__result__indicator__period__target(result_indicator_period_target)

        result_period = self.parser_201.get_model('ResultIndicatorPeriod')
        self.assertEquals(str(result_period.target), attrs['value'])

    def test_result_indicator_period_target_comment_201(self):
        """
        test for result_indicator_period_target_comment + accompanying narrative
        """

        test_result_indicator_period = iati_factory.ResultIndicatorPeriodFactory.build()
        self.parser_201.register_model('ResultIndicatorPeriod', test_result_indicator_period)

        result_indicator_period_target_comment = E('comment') 
        self.parser_201.iati_activities__iati_activity__result__indicator__period__target__comment(result_indicator_period_target_comment)

        result_indicator_period_target_comment = self.parser_201.get_model('ResultIndicatorPeriodTargetComment')
        self.assertEquals(result_indicator_period_target_comment.result_indicator_period, test_result_indicator_period)

        self.parser_201.iati_activities__iati_activity__result__indicator__period__target__comment__narrative(self.narrative)
        narrative = self.parser_201.get_model('ResultIndicatorPeriodTargetCommentNarrative')
        self.assertEquals(narrative.related_object, result_indicator_period_target_comment)

    def test_result_indicator_period_target_comment_105(self):
        """
        test for result_indicator_period_target_comment + accompanying narrative
        """

        test_result_indicator_period = iati_factory.ResultIndicatorPeriodFactory.build()
        self.parser_105.register_model('ResultIndicatorPeriod', test_result_indicator_period)

        result_indicator_period_target_comment = E('comment', 'some description') 
        self.parser_105.iati_activities__iati_activity__result__indicator__period__target__comment(result_indicator_period_target_comment)

        result_indicator_period_target_comment = self.parser_105.get_model('ResultIndicatorPeriodTargetComment')
        self.assertEquals(result_indicator_period_target_comment.result_indicator_period, test_result_indicator_period)

        narrative = self.parser_105.get_model('ResultIndicatorPeriodTargetCommentNarrative')
        self.assertEquals(narrative.related_object, result_indicator_period_target_comment)

    def test_result_indicator_period_actual(self):
        """
        test for result_indicator_period_actual + accompanying narrative
        """

        attrs = {
            'value': '100'
        }

        result_indicator_period_actual = E('actual', **attrs) 
        self.parser_201.iati_activities__iati_activity__result__indicator__period__actual(result_indicator_period_actual)

        result_period = self.parser_201.get_model('ResultIndicatorPeriod')
        self.assertEquals(str(result_period.actual), attrs['value'])

    def test_result_indicator_period_actual_comment_201(self):
        """
        test for result_indicator_period_actual_comment + accompanying narrative
        """

        test_result_indicator_period = iati_factory.ResultIndicatorPeriodFactory.build()
        self.parser_201.register_model('ResultIndicatorPeriod', test_result_indicator_period)

        result_indicator_period_actual_comment = E('comment') 
        self.parser_201.iati_activities__iati_activity__result__indicator__period__actual__comment(result_indicator_period_actual_comment)

        result_indicator_period_actual_comment = self.parser_201.get_model('ResultIndicatorPeriodActualComment')
        self.assertEquals(result_indicator_period_actual_comment.result_indicator_period, test_result_indicator_period)

        self.parser_201.iati_activities__iati_activity__result__indicator__period__actual__comment__narrative(self.narrative)
        narrative = self.parser_201.get_model('ResultIndicatorPeriodActualCommentNarrative')
        self.assertEquals(narrative.related_object, result_indicator_period_actual_comment)

    def test_result_indicator_period_actual_comment_105(self):
        """
        test for result_indicator_period_actual_comment + accompanying narrative
        """

        test_result_indicator_period = iati_factory.ResultIndicatorPeriodFactory.build()
        self.parser_105.register_model('ResultIndicatorPeriod', test_result_indicator_period)

        result_indicator_period_actual_comment = E('comment', 'some description') 
        self.parser_105.iati_activities__iati_activity__result__indicator__period__actual__comment(result_indicator_period_actual_comment)

        result_indicator_period_actual_comment = self.parser_105.get_model('ResultIndicatorPeriodActualComment')
        self.assertEquals(result_indicator_period_actual_comment.result_indicator_period, test_result_indicator_period)

        narrative = self.parser_105.get_model('ResultIndicatorPeriodActualCommentNarrative')
        self.assertEquals(narrative.related_object, result_indicator_period_actual_comment)

