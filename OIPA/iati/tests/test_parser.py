"""
    Unit tests for all fields in the parser, for multiple IATI versions.
"""

import copy
import datetime
from django.core import management
from iati.factory import iati_factory

from django.test import TestCase as DjangoTestCase # Runs each test in a transaction and flushes database
from unittest import TestCase

from lxml import etree
from lxml.builder import E

from iati.iati_parser import ParseIATI

from iati_synchroniser.models import IatiXmlSource, Publisher
import iati.models as iati_models
import iati_codelists.models as codelist_models

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

def print_xml(elem):
    print(etree.tostring(elem, pretty_print=True))

def build_activity(version="2.01"):
        activity = iati_factory.ActivityFactory.build(
            iati_standard_version_id=codelist_models.Version.objects.get(code=version) # TODO: cache this
        )
        return activity

class ParserSetupTestCase(DjangoTestCase):

    fixtures = ['test_publisher.json', 'test_codelists.json']

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

        # todo: self.assertTrue source was handled appropriately
        # self.self.assertTrueEqual(self.parser_103.iati_source, self.parser_104.iati_source, self.parser_105.iati_source, self.parser_201.iati_source)

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
            "default-currency": "USD",
            "last-updated-datetime": datetime.datetime.now().isoformat(' '),
            "linked-data-uri": "http://zimmermanzimmerman.org/iati",
            "hierarchy": "1"
        }

        # default activity model fields
        self.defaults = {
            "hierarchy": 1,
            "default_lang": "en",
        }

        iati_activity = E("iati-activity", **self.attrs)
        iati_activity.append(E("iati-identifier", self.iati_identifier))
        self.iati_201.append(iati_activity) 
        self.iati_201.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en" # ISO 639-1:2002
        # print(etree.tostring(self.iati_201, pretty_print=True))

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
        self.assertTrue(activity.default_lang == "en")
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
        self.assertTrue(activity.default_lang == "en")
        self.assertTrue(activity.iati_standard_version.code == "2.01")

    def test_activity_no_last_updated_datetime(self):
        """
        case 1: new activity.last_updated_datetime >= old activity.last_updated_datetime => parse new activity
        case 2: new activity.last_updated_datetime < old activity.last_updated_datetime => Don't parse new activity
        case 3: new activity.last_updated_datetime is absent and old activity.last_updated_datetime is present => Don't parse
        case 4: new activity.last_updated_datetime is absent and old activity.last_updated_datetime is absent => Parse
        """
        old_activity = copy_xml_tree(self.iati_201).find('iati-activity')
        new_activity = copy_xml_tree(self.iati_201).find('iati-activity')

        iati_identifier = new_activity.find('iati-identifier')
        iati_identifier.text = self.alt_iati_identifier

        def check_parsed(old_activity, new_activity, overwrites=True):
            self.parser_201.iati_activities__iati_activity(old_activity)
            self.parser_201.iati_activities__iati_activity(new_activity)

            activity = self.parser_201.get_model('Activity')

            if overwrites:
                self.assertTrue(activity.id == new_activity.xpath('iati-identifier/text()')[0])
            else:
                self.assertTrue(activity.id == old_activity.xpath('iati-identifier/text()')[0] )


        # case 1 (greater)
        old_activity.attrib["last_updated_datetime"] = (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat() 
        new_activity.attrib["last_updated_datetime"] = datetime.datetime.now().isoformat()
        check_parsed(old_activity, new_activity, True)

        # case 1 (equivalence)
        time = datetime.datetime.now().isoformat()
        old_activity.attrib["last_updated_datetime"] = time
        new_activity.attrib["last_updated_datetime"] = time
        check_parsed(old_activity, new_activity, True)

        # case 2
        old_activity.attrib["last_updated_datetime"] = datetime.datetime.now().isoformat()
        new_activity.attrib["last_updated_datetime"] = (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat() 
        check_parsed(old_activity, new_activity, False)

        # case 3
        old_activity.attrib["last_updated_datetime"] = datetime.datetime.now().isoformat()
        new_activity.attrib["last_updated_datetime"] = None
        check_parsed(old_activity, new_activity, False)

        # case 4
        old_activity.attrib["last_updated_datetime"] = None
        new_activity.attrib["last_updated_datetime"] = None
        check_parsed(old_activity, new_activity, True)

    def test_activity_linked_data_uri_inherited(self):
        """
        Check linked-data-uri is inherited from iati-activities if set
        """
        linked_data_default ="http://zimmermanzimmerman.org/"

        iati_201 = copy_xml_tree(self.iati_201)
        iati_201.set("linked-data-default", linked_data_default)

        iati_activity = iati_201.find('iati-activity')
        del iati_activity.attrib['linked-data-uri']

        self.parser_201.iati_activities__iati_activity(iati_201)
        activity = self._get_activity(self.iati_identifier)

        self.assertTrue(activity.linked_data_uri == linked_data_default)

    def test_iati_identifier(self):
        """
        iati_activities__iati_activity__iati_identifier
        should raise exception if not present
        """
        iati_201 = copy_xml_tree(self.iati_201)
        iati_identifier = iati_201.find('iati-activity').find('iati-identifier')

        activity = iati_factory.ActivityFactory.build()
        
        self.parser_201.register_model('Activity', activity)
        self.parser_201.iati_activities__iati_activity__iati_identifier(iati_identifier)
        activity = self.parser_201.get_model('Activity')

        self.assertTrue(activity.iati_identifier == iati_identifier.text)

        # empty iati-idenifier should throw exception
        iati_identifier.text = ""

        self.parser_201.iati_activities__iati_activity__iati_identifier(iati_identifier)
        activity = self.parser_201.get_model('Activity')

        with self.self.assertTrueRaises(Exception):
            activity.save()

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
            iati_standard_version_id=codelist_models.Version.objects.get(code="2.01")
        )

        self.parser_201.register_model('Activity', activity)
        self.parser_201.iati_activities__iati_activity__capital_spend(capital_spend)
        activity = self.parser_201.get_model('Activity')

        self.assertTrue(activity.capital_spend == percentage)


    def test_has_conditions_returns_true(self):
        attached = '1'

        iati_activity = copy_xml_tree(self.iati_201).find("iati-activity")
        iati_activity.append(E('conditions', attached=attached))
        conditions = iati_activity.find('conditions')
        
        activity = iati_factory.ActivityFactory.build(
            iati_standard_version_id=codelist_models.Version.objects.get(code="2.01")
        )

        self.parser_201.register_model('Activity', activity)
        self.parser_201.iati_activities__iati_activity__conditions(conditions)
        activity = self.parser_201.get_model('Activity')
        activity.save()

        self.assertTrue(activity.has_conditions == True)

    def test_has_conditions_returns_false(self):
        attached = '0'

        iati_activity = copy_xml_tree(self.iati_201).find("iati-activity")
        iati_activity.append(E('conditions', attached=attached))
        conditions = iati_activity.find('conditions')
        
        activity = iati_factory.ActivityFactory.build(
            iati_standard_version_id=codelist_models.Version.objects.get(code="2.01")
        )

        self.parser_201.register_model('Activity', activity)
        self.parser_201.iati_activities__iati_activity__conditions(conditions)
        activity = self.parser_201.get_model('Activity')
        activity.save()

        self.assertTrue(activity.has_conditions == False)

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
        narrative = self.parser_201.get_model('Narrative')

        self.assertTrue(narrative.parent_object == title)

    def test_title_105(self):
        self.title.text = "random text"
        self.parser_105.iati_activities__iati_activity__title(self.title)

        title = self.parser_105.get_model('Title')
        narrative = self.parser_105.get_model('Narrative')

        self.assertTrue(title.activity == self.activity)
        self.assertTrue(narrative.parent_object == title)

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
        narrative = self.parser_201.get_model('Narrative')

        self.assertTrue(narrative.parent_object == description)

    def test_description_105(self):
        self.description.text = "random text"
        self.parser_105.iati_activities__iati_activity__description(self.description)

        description = self.parser_105.get_model('Description')
        narrative = self.parser_105.get_model('Narrative')

        self.assertTrue(description.activity == self.activity)
        self.assertTrue(narrative.parent_object == description)

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
        self.parent_object = build_activity()

    def addForeignKeyDefaultNarrative(self):
        """
        Given an arbitrary foreign key, the narrative should be created and be queryable using default assumed values (language)
        """
        self.parser_201.add_narrative(self.narrative, self.parent_object)
        narrative = self.parser_201.get_model('Narrative')

        self.assertTrue(narrative.parent_object == self.parent_object)
        self.assertTrue(narrative.content == self.test_text)
        self.assertTrue(narrative.language.code == self.defaults["language"])


    def addForeignKeyNonDefaultLanguageNarrative(self):
        """
        The narrative should change its language parameter based on the xml:lang element 
        """
        self.narrative.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "fr" # ISO 639-1:2002

        self.parser_201.add_narrative(self.narrative, self.parent_object)
        narrative = self.parser_201.get_model('Narrative')

        self.assertTrue(narrative.language.code == "fr")

# Todo: after organization implementation
class OrganisationTestCase(ParserSetupTestCase):
    pass

class ActivityReportingOrganisation(ParserSetupTestCase):
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
        }

        self.reporting_org = E('reporting-org', **self.attrs)

    def test_organisation_not_parsed_yet(self):
        """
        Check element is parsed correctly, excluding narratives when organisation is not in the organisation API. This results in the organisation field being empty
        """
        activity = build_activity(version="2.01")
        self.parser_201.register_model('Activity', activity)

        self.parser_201.iati_activities__iati_activity__reporting_org(self.reporting_org)

        reporting_organisation = self.parser_201.get_model('ActivityReportingOrganisation')

        self.assertTrue(reporting_organisation.ref == self.attrs["ref"])
        self.assertTrue(reporting_organisation.type.code == int(self.attrs["type"]))
        self.assertTrue(reporting_organisation.activity == activity)
        self.assertTrue(reporting_organisation.organisation == None)
        self.assertTrue(reporting_organisation.secondary_reporter == bool(int(self.attrs["secondary-reporter"])))

    def test_organisation_already_parsed(self):
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
        self.assertTrue(reporting_organisation.organisation.code == test_organisation.code)
        self.assertTrue(reporting_organisation.type.code == int(self.attrs["type"]))
        self.assertTrue(reporting_organisation.secondary_reporter == bool(int(self.attrs["secondary-reporter"])))



