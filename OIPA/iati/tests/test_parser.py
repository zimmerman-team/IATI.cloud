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

    fixtures = ['test_publisher.json', 'test_codelists.json', 'test_vocabulary', 'test_geodata.json']

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

        activity = build_activity(version="2.01")
        self.parser_201.register_model('Activity', activity)

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

        # case 1 (equivalence)
        time = datetime.datetime.now().isoformat()
        old_activity.attrib["last-updated-datetime"] = time
        new_activity.attrib["last-updated-datetime"] = time
        self.check_parsed(old_activity, new_activity, True)

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

    def test_activity_linked_data_uri_inherited(self):
        """
        Check linked-data-uri is inherited from iati-activities if set
        """
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
        
        activity = build_activity(version="2.01")

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
        
        activity = build_activity(version="2.01")

        self.parser_201.register_model('Activity', activity)
        self.parser_201.iati_activities__iati_activity__conditions(conditions)
        activity = self.parser_201.get_model('Activity')
        print(activity)
        print(activity.last_updated_datetime)
        activity.save()

        self.assertTrue(activity.has_conditions == False)

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
        narrative = self.parser_201.get_model('Narrative')

        self.assertTrue(narrative.parent_object == other_identifier)

    def test_other_identifier_105(self):
        """
        If other-identifier is present then either @owner-ref or @owner-name must be present
        """
        self.parser_105.iati_activities__iati_activity__other_identifier(self.other_identifier_105)
        other_identifier = self.parser_105.get_model('OtherIdentifier')

        self.assertTrue(other_identifier.activity == self.activity)
        self.assertTrue(other_identifier.identifier == "Some-ref")
        self.assertTrue(other_identifier.owner_ref == self.owner_org_xml['ref'])

        narrative = self.parser_105.get_model('Narrative')
        self.assertTrue(narrative.parent_object == other_identifier)

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
        }

        self.reporting_org = E('reporting-org', **self.attrs)

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
        self.assertTrue(reporting_organisation.organisation == None)
        self.assertTrue(reporting_organisation.secondary_reporter == bool(self.attrs["secondary-reporter"]))

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
        self.assertTrue(reporting_organisation.organisation.code == test_organisation.code)
        self.assertTrue(reporting_organisation.type.code == self.attrs["type"])
        self.assertTrue(reporting_organisation.secondary_reporter == bool(self.attrs["secondary-reporter"]))

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
        self.participating_org_105 = E('participating-org', **self.attrs_105)

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
        self.assertTrue(participating_organisation.organisation.code == test_organisation.code)
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

    def test_participating_organisation_already_parsed_105(self):
        """
        Check complete element is parsed correctly, excluding narratives when the organisation is available in the Organisation standard (and hence is pared)
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
        self.assertTrue(participating_organisation.organisation.code == test_organisation.code)
        self.assertTrue(participating_organisation.type.code == self.attrs_105["type"])
        self.assertTrue(participating_organisation.role.code == self.attrs_201["role"])


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
        narrative = self.parser_201.get_model('Narrative')

        self.assertTrue(narrative.parent_object == activity_date)

    def test_activity_date_105(self):
        """
        If other-identifier is present then either @owner-ref or @owner-name must be present
        """
        self.parser_105.iati_activities__iati_activity__activity_date(self.activity_date_105)
        activity_date = self.parser_105.get_model('ActivityDate')

        self.assertTrue(activity_date.activity == self.activity)
        self.assertTrue(str(activity_date.iso_date) == self.attrs_201['iso-date'])
        self.assertTrue(activity_date.type.code == self.attrs_201['type'])

        narrative = self.parser_105.get_model('Narrative')
        self.assertTrue(narrative.parent_object == activity_date)

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

    def test_contact_info_201(self):
        """
        Only defines the type field
        """
        self.parser_201.iati_activities__iati_activity__contact_info(self.contact_info)
        contact_info = self.parser_201.get_model('ContactInfo')

        self.assertTrue(contact_info.activity == self.activity)
        self.assertTrue(contact_info.type.code == self.attrs['type'])

    def test_contact_info_organisation_201(self):
        """
        Along with narrative
        """
        contact_organisation = E('organisation', **self.attrs)
        self.parser_201.iati_activities__iati_activity__contact_info__organisation(contact_organisation)
        contact_info_organisation = self.parser_201.get_model('ContactInfoOrganisation')

        self.assertTrue(contact_info_organisation.contact_info == self.test_contact_info)

        self.parser_201.iati_activities__iati_activity__contact_info__organisation__narrative(self.narrative)
        narrative = self.parser_201.get_model('Narrative')
        self.assertTrue(narrative.parent_object == contact_info_organisation)

    def test_contact_info_organisation_105(self):
        """
        Along with narrative
        """
        contact_organisation = E('organisation', 'some description')
        self.parser_105.iati_activities__iati_activity__contact_info__organisation(contact_organisation)
        contact_info_organisation = self.parser_201.get_model('ContactInfoOrganisation')

        self.assertTrue(contact_info_organisation.contact_info == self.test_contact_info)
        narrative = self.parser_105.get_model('Narrative')
        self.assertTrue(narrative.parent_object == contact_info_organisation)

    def test_contact_info_department(self):
        """
        Along with narrative
        """
        contact_department = E('department', **self.attrs)
        self.parser_201.iati_activities__iati_activity__contact_info__department(contact_department)
        contact_info_department = self.parser_201.get_model('ContactInfoDepartment')

        self.assertTrue(contact_info_department.contact_info == self.test_contact_info)

        self.parser_201.iati_activities__iati_activity__contact_info__department__narrative(self.narrative)
        narrative = self.parser_201.get_model('Narrative')
        self.assertTrue(narrative.parent_object == contact_info_department)

    def test_contact_info_department_105(self):
        """
        Along with narrative
        """
        contact_department = E('department', 'some description')
        self.parser_105.iati_activities__iati_activity__contact_info__department(contact_department)
        contact_info_department = self.parser_201.get_model('ContactInfoDepartment')

        self.assertTrue(contact_info_department.contact_info == self.test_contact_info)
        narrative = self.parser_105.get_model('Narrative')

    def test_contact_info_person_name(self):
        """
        Along with narrative
        """
        contact_person_name = E('person-name', **self.attrs)
        self.parser_201.iati_activities__iati_activity__contact_info__person_name(contact_person_name)
        contact_info_person_name = self.parser_201.get_model('ContactInfoPersonName')

        self.assertTrue(contact_info_person_name.contact_info == self.test_contact_info)

        self.parser_201.iati_activities__iati_activity__contact_info__person_name__narrative(self.narrative)
        narrative = self.parser_201.get_model('Narrative')
        self.assertTrue(narrative.parent_object == contact_info_person_name)

    def test_contact_info_person_name_105(self):
        """
        Along with narrative
        """
        contact_person_name = E('person_name', 'some description')
        self.parser_105.iati_activities__iati_activity__contact_info__person_name(contact_person_name)
        contact_info_person_name = self.parser_201.get_model('ContactInfoPersonName')

        self.assertTrue(contact_info_person_name.contact_info == self.test_contact_info)
        narrative = self.parser_105.get_model('Narrative')

    def test_contact_info_job_title(self):
        """
        Along with narrative
        """
        contact_job_title = E('job-title', **self.attrs)
        self.parser_201.iati_activities__iati_activity__contact_info__job_title(contact_job_title)
        contact_info_job_title = self.parser_201.get_model('ContactInfoJobTitle')

        self.assertTrue(contact_info_job_title.contact_info == self.test_contact_info)

        self.parser_201.iati_activities__iati_activity__contact_info__job_title__narrative(self.narrative)
        narrative = self.parser_201.get_model('Narrative')
        self.assertTrue(narrative.parent_object == contact_info_job_title)

    def test_contact_info_job_title_105(self):
        """
        Along with narrative
        """
        contact_job_title = E('job_title', 'some description')
        self.parser_105.iati_activities__iati_activity__contact_info__job_title(contact_job_title)
        contact_info_job_title = self.parser_201.get_model('ContactInfoJobTitle')

        self.assertTrue(contact_info_job_title.contact_info == self.test_contact_info)
        narrative = self.parser_105.get_model('Narrative')

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
        narrative = self.parser_201.get_model('Narrative')
        self.assertTrue(narrative.parent_object == contact_info_mailing_address)

    def test_contact_info_mailing_address_105(self):
        """
        Along with narrative
        """
        contact_mailing_address = E('mailing_address', 'some description')
        self.parser_105.iati_activities__iati_activity__contact_info__mailing_address(contact_mailing_address)
        contact_info_mailing_address = self.parser_201.get_model('ContactInfoMailingAddress')

        self.assertTrue(contact_info_mailing_address.contact_info == self.test_contact_info)

        narrative = self.parser_105.get_model('Narrative')
        self.assertTrue(narrative.parent_object == contact_info_mailing_address)

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
        narrative = self.parser_201.get_model('Narrative')
        self.assertTrue(narrative.parent_object == location_name)

    def test_location_name_105(self):
        location_name = E('name', "some text")
        self.parser_105.iati_activities__iati_activity__location__name(location_name)
        location_name = self.parser_105.get_model('LocationName')

        self.assertTrue(location_name.location == self.test_location)
        narrative = self.parser_105.get_model('Narrative')
        self.assertTrue(narrative.parent_object == location_name)

    def test_location_description_201(self):
        """
        Including narratives
        """
        location_description = E('description')
        self.parser_201.iati_activities__iati_activity__location__description(location_description)
        location_description = self.parser_201.get_model('LocationDescription')

        self.assertTrue(location_description.location == self.test_location)

        self.parser_201.iati_activities__iati_activity__location__description__narrative(self.narrative)
        narrative = self.parser_201.get_model('Narrative')
        self.assertTrue(narrative.parent_object == location_description)

    def test_location_activity_description_201(self):
        """
        Including narratives
        """
        activity_description = E('activity-description')
        self.parser_201.iati_activities__iati_activity__location__activity_description(activity_description)
        activity_description = self.parser_201.get_model('LocationActivityDescription')

        self.assertTrue(activity_description.location == self.test_location)

        self.parser_201.iati_activities__iati_activity__location__activity_description__narrative(self.narrative)
        narrative = self.parser_201.get_model('Narrative')
        self.assertTrue(narrative.parent_object == activity_description)

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

        self.assertTrue(location.point_pos.coords == (31.616944, 65.716944))

    # TODO : test for latlong validation
    # def test_location_pos_pos_invalid_latlong_201(self):
    #     pos = E('pos', '91.616944 328392189031283.716944')
    #     with self.assertRaises(self.parser_201.ValidationError):
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
        self.assertTrue(location.point_pos.coords == (31.616944, 65.716944))
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
            "gazetteer-ref": "1"
        }
        gazetteer = E('gazetteer-entry', "some code", **props) # Geonames.org
        self.parser_103.iati_activities__iati_activity__location__gazetteer_entry(gazetteer)
        location = self.parser_103.get_model('Location')

        self.assertTrue(location.location_id_code == "some code")
        self.assertTrue(location.location_id_vocabulary.code == "G1")

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
        narrative = self.parser_201.get_model('Narrative')
        self.assertTrue(narrative.parent_object == budget_item_description)

    def test_budget_item_description_105(self):
        budget_item = iati_factory.BudgetItemFactory.build()
        self.parser_105.register_model('BudgetItem', budget_item)

        budget_item_description = E('description', "some text", code="1.1.1", percentage="50.21") # Executive - executive
        self.parser_105.iati_activities__iati_activity__country_budget_items__budget_item__description(budget_item_description)
        budget_item_description = self.parser_105.get_model('BudgetItemDescription')

        self.assertTrue(budget_item_description.budget_item == budget_item)

        narrative = self.parser_105.get_model('Narrative')
        self.assertTrue(narrative.parent_object == budget_item_description)

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
        narrative = self.parser_201.get_model('Narrative')
        self.assertTrue(narrative.parent_object == activity_policy_marker)

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

        narrative = self.parser_105.get_model('Narrative')
        self.assertTrue(narrative.parent_object == activity_policy_marker)
