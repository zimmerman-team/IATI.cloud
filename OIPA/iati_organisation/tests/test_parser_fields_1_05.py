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

from iati.parser.iati_parser import ParseIATI

from iati_synchroniser.models import IatiXmlSource, Publisher
import iati.models as iati_models
import iati_codelists.models as codelist_models
import iati_organisation.models as org_models
from geodata.models import Country
from iati.factory import iati_factory

from iati.parser.IATI_1_03 import Parse as Parser_103
from iati.parser.IATI_1_05 import Parse as Parser_105
from iati_organisation.organisation_1_05 import Parse as OrgParse_105


def build_xml(version, organisation_identifier):
    """
        Construct a base activity file to work with in the tests
    """

    activities_attrs = { "generated-datetime": datetime.datetime.now().isoformat(),
        "version": version,

    }

    activity = E("iati-organisations",
        **activities_attrs
    )

    return activity

def copy_xml_tree(tree):
    return copy.deepcopy(tree)

def print_xml(elem):
    print(etree.tostring(elem, pretty_print=True))

# TODO: Get rid of fixtures - 2016-04-21
def setUpModule():
    fixtures = ['test_publisher.json', 'test_codelists.json', 'test_vocabulary', 'test_geodata.json']

    for fixture in fixtures:
        management.call_command("loaddata", fixture)

def tearDownModule():
    management.call_command('flush', interactive=False, verbosity=0)

class ParserSetupTestCase(DjangoTestCase):

    @classmethod
    def setUpClass(self):
        # for fixture in self.fixtures:
        #     management.call_command("loaddata", fixture)

        self.iati_identifier = "NL-KVK-51018586-0666"

        self.iati_105 = build_xml("1.05", self.iati_identifier)

        dummy_source = IatiXmlSource.objects.get(id=2)

        self.parser_105 = ParseIATI(dummy_source, self.iati_105).get_parser()

        assert(isinstance(self.parser_105, OrgParse_105))

    @classmethod
    def tearDownClass(self):
        pass

class OrganisationTestCase(ParserSetupTestCase):
    """
    iati_activities__iati_activity
    CHANGELOG
    2.01: The version attribute was removed.
    1.02: Introduced the linked-data-uri attribute on iati-activity element
    """
    def setUp(self):
        # sample attributes on iati-activity xml
        self.attrs = {
            "default-currency": "USD",
            "last-updated-datetime": datetime.datetime.now().isoformat(' '),
        }

        # default activity model fields
        self.defaults = {
            "hierarchy": 1,
        }

        # iati_organisation = E("iati-organisation", **self.attrs)
        # iati_organisation.append(E("organisation-identifier", self.iati_identifier))

        self.organisation = iati_factory.OrganisationFactory.create()
        self.parser_105.default_lang = "en"
        self.parser_105.register_model('Organisation', self.organisation)

    def test_iati_organisations__iati_organisation(self):
        attribs = {
                'default-currency':'EUR',
                'last-updated-datetime':'2014-09-10T07:15:37Z',
                '{http://www.w3.org/XML/1998/namespace}lang':'en',
                }

        element = E('iati-organisation', E('iati-identifier','test-id',{}),attribs)

        self.parser_105.iati_organisations__iati_organisation(element)

        organisation = self.parser_105.get_model('Organisation')

        self.assertEqual(organisation.id, 'test-id')
        self.assertEqual(organisation.default_currency_id , attribs['default-currency'])
        self.assertEqual(organisation.last_updated_datetime, self.parser_105.validate_date(attribs['last-updated-datetime']))

    def test_iati_organisations__iati_organisation__name(self):
        element = E('name', 'test narrative name')

        self.parser_105.iati_organisations__iati_organisation__name(element)

        narrative = self.parser_105.get_model('OrganisationNameNarrative')

        print(narrative)
        self.assertEqual('test narrative name', narrative.content)

