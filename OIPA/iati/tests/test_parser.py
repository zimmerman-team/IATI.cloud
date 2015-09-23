"""
    Unit tests for all fields in the parser, for multiple IATI versions.
"""

import copy
import datetime
from django.core import management

from django.test import TestCase as DjangoTestCase # Runs each test in a transaction and flushes database
from unittest import TestCase 

from lxml import etree
from lxml.builder import E

from iati.iati_parser import ParseIATI

from iati_synchroniser.models import IatiXmlSource, Publisher
import iati.models as iati_models

from iati.IATI_1_03 import Parse as Parser_103
from iati.IATI_1_05 import Parse as Parser_105
from iati.IATI_2_01 import Parse as Parser_201


def build_xml(version, iati_identifier):
    """
        Construct a base activity file to work with in the tests
    """

    activities_attrs = { "generated-datetime": datetime.datetime.now().isoformat(),
        "version": version,
        "linked-data-default": "http://zimmermanzimmerman.org/",
    }

    activity = E("iati-activities", 
        E("iati-activity"),
        E("iati-identifier", iati_identifier), # nescessary
        **activities_attrs
    )
    
    return activity

def create_dummy_source(url, title, name, current_publisher, cur_type):
    source = IatiXmlSource(
        ref=name,
        title=title,
        publisher=current_publisher,
        source_url=url,
        type=cur_type)

    source.save(process=False, added_manually=False)
    return source

def copy_xml_tree(tree):
    return copy.deepcopy(tree)

class ParserSetupTestCase(DjangoTestCase):

    fixtures = ['test_publisher.json',]

    def _get_activity(self, iati_identifier):
        return iati_models.Activity.objects.get(id=iati_identifier)

    @classmethod
    def setUpClass(self):
        # load fixtures
        for fixture in self.fixtures:
            management.call_command("loaddata", fixture)

        self.iati_identifier = "NL-KVK-51018586-0666"
        self.alt_iati_identifier = "NL-KVK-51018586-0667"

        self.iati_103 = build_xml("1.03", self.iati_identifier)
        self.iati_104 = build_xml("1.04", self.iati_identifier)
        self.iati_105 = build_xml("1.05", self.iati_identifier)
        self.iati_201 = build_xml("2.01", self.iati_identifier)

        # publisher = Publisher.objects.get(id=1) # from fixture
        # dummy_source = create_dummy_source("http://zimmermanzimmerman.org/iati", "ZnZ", "Zimmerman", publisher, 1)
        dummy_source = IatiXmlSource.objects.get(id=1)

        parseIati = ParseIATI()
        self.parser_103 = parseIati.prepare_parser(self.iati_103, dummy_source)
        self.parser_104 = parseIati.prepare_parser(self.iati_104, dummy_source)
        self.parser_105 = parseIati.prepare_parser(self.iati_105, dummy_source)
        self.parser_201 = parseIati.prepare_parser(self.iati_201, dummy_source)

        assert(isinstance(self.parser_103, Parser_103))
        assert(isinstance(self.parser_104, Parser_105))
        assert(isinstance(self.parser_105, Parser_105))
        assert(isinstance(self.parser_201, Parser_201))

        # todo: assert source was handled appropriately
        # self.assertEqual(self.parser_103.iati_source, self.parser_104.iati_source, self.parser_105.iati_source, self.parser_201.iati_source)

    @classmethod
    def tearDownClass(self):
        pass


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
            "default_currency": "USD",
            "last-updated-datetime": datetime.datetime.now().isoformat(),
            "linked-data-uri": "http://zimmermanzimmerman.org/iati",
            "hierarchy": "1"
        }

        # default activity model fields
        self.defaults = {
            "hierarchy": 1,
            "default_lang": "en",
        }

        self.iati_201.append(E("iati-activity", **self.attrs)) 
        self.iati_201.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en" # ISO 639-1:2002
        print(etree.tostring(self.iati_201, pretty_print=True))

    def test_activity_201(self):
        """
        Check complete element is parsed correctly
        """
        self.parser_201.iati_activities__iati_activity(self.iati_201)

        activity = self._get_activity(self.iati_identifier)

        for field, attr in self.attrs.iteritems():
            assert(activity[field] == attr)
        assert(activity.default_lang == "en")
        assert(activity.iati_standard_version == "2.01")

    def test_activity_default_201_test(self):
        """
        Check defaults are set accordingly
        """
        iati_201 = copy_xml_tree(self.iati_201)
        iati_activity = iati_201.xpath('iati_activity') 
        del iati_activity.attrib('default_currency')
        del iati_activity.attrib('last_updated_datetime')
        del iati_activity.attrib('xml:lang')
        del iati_activity.attrib('hierarchy')
        del iati_activity.attrib('linked-data-uri')

        self.parser_201.iati_activities__iati_activity(iati_201)

        activity = self._get_activity(self.iati_identifier)

        for field, default in self.defaults.iteritems():
            assert(activity[field] == default)
        assert(activity.default_lang == "en")
        assert(activity.iati_standard_version == "2.01")

    def test_activity_no_last_updated_datetime(self):
        """
        case 1: new activity.last_updated_datetime >= old activity.last_updated_datetime => parse new activity
        case 2: new activity.last_updated_datetime < old activity.last_updated_datetime => Don't parse new activity
        case 3: new activity.last_updated_datetime is absent and old activity.last_updated_datetime is present => Don't parse
        case 4: new activity.last_updated_datetime is absent and old activity.last_updated_datetime is absent => Parse
        """
        old_activity = copy_xml_tree(self.iati_201)
        new_activity = copy_xml_tree(self.iati_201)
        iati_identifier = new_activity.xpath('iati-identifier')
        iati_identifier.text = self.alt_iati_identifier

        def check_parsed(overwrites=True, old_activity, new_activity):
            self.parser_201.iati_activities__iati_activity(old_activity)
            self.parser_201.iati_activities__iati_activity(new_activity)

            activity = self._get_activity(self.iati_identifier)
            if overwrites:
                assert(activity.iati_identifier == new_activity.xpath('iati-identifier/text()')[0])
            else:
                assert(activity.iati_identifier == old_activity.xpath('iati-identifier/text()')[0] )


        # case 1 (greater)
        old_activity.attrib["last_updated_datetime"] = datetime.datetime.now().AddDays(-1).isoformat()
        new_activity.attrib["last_updated_datetime"] = datetime.datetime.now().isoformat()
        check_parsed(True, old_activity, new_activity)

        # case 1 (equivalence)
        time = datetime.datetime.now().isoformat()
        old_activity.attrib["last_updated_datetime"] = time
        new_activity.attrib["last_updated_datetime"] = time
        check_parsed(True, old_activity, new_activity)

        # case 2
        old_activity.attrib["last_updated_datetime"] = datetime.datetime.now().isoformat()
        new_activity.attrib["last_updated_datetime"] = datetime.datetime.now().AddDays(-1).isoformat()
        check_parsed(False, old_activity, new_activity)

        # case 3
        old_activity.attrib["last_updated_datetime"] = datetime.datetime.now().isoformat()
        new_activity.attrib["last_updated_datetime"] = None
        check_parsed(False, old_activity, new_activity)

        # case 4
        old_activity.attrib["last_updated_datetime"] = None
        new_activity.attrib["last_updated_datetime"] = None
        check_parsed(True, old_activity, new_activity)

    def test_activity_linked_data_uri_inherited(self):
        """
        Check linked-data-uri is inherited from iati-activities if set
        """
        iati_201 = copy_xml_tree(self.iati_201)
        del iati_activity.attrib('linked-data-uri')

        linked_data_default = iati_201.attrib['linked-data-default']

        self.parser_201.iati_activities__iati_activity(iati_201)
        activity = self._get_activity(self.iati_identifier)

        assert(activity.linked_data_uri == linked_data_default)

    def test_iati_identifier(self):
        """
        iati_activities__iati_activity__iati_identifier
        should raise exception if not present
        """
        iati_201 = copy_xml_tree(self.iati_201)
        iati_identifier = iati_201.xpath('iati-identifier')

        self.parser_201.iati_activities__iati_activity(iati_201)

        activity = self.parser_201.get_model('Activity')

        assert(activity.iati_identifier == iati_identifier.text)

        # empty iati-idenifier
        iati_identifier.text = ""
        self.parser_201.iati_activities__iati_activity(iati_201)

        with self.assertRaise(Exception):
            activity.save()

    def test_capital_spend(self):
        """
        iati_activities__capital_spend
        CHANGELOG
        1.03: This is a new element, introduced in version 1.03 of the standard
        """
        percentage = "80"

        iati_201 = copy_xml_tree(self.iati_201)
        iati_201.append(E('capital-spend', percentage=percentage))

        self.parser_201.iati_activities__iati_activity(iati_201)
        activity = self._get_activity(self.iati_identifier)

        assert(activity.percentage)


    def test_has_conditions(self):


# Todo: after organization implementation
class OrganisationTestCase(ParserSetupTestCase):
    pass

class 

