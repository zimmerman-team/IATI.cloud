"""
    Unit tests for all fields in the parser, for multiple IATI versions.
"""

import copy
import datetime

import pytest
from django.core import management
# Runs each test in a transaction and flushes database
from django.test import TestCase
from lxml.builder import E

from iati.factory import iati_factory
from iati.parser.parse_manager import ParseManager
from iati_organisation.parser.organisation_1_05 import Parse as OrgParse_105
from iati_synchroniser.factory import synchroniser_factory


def build_xml(version, organisation_identifier):
    """
        Construct a base activity file to work with in the tests
    """

    activities_attrs = {
        "generated-datetime": datetime.datetime.now().isoformat(),
        "version": version,
    }

    activity = E("iati-organisations",
                 **activities_attrs
                 )

    return activity


def copy_xml_tree(tree):
    return copy.deepcopy(tree)

# TODO: Get rid of fixtures - 2016-04-21


@pytest.fixture(scope='session')
def setUpModule():
    fixtures = ['test_vocabulary', 'test_codelists.json', 'test_geodata.json']

    for fixture in fixtures:
        management.call_command("loaddata", fixture)


def tearDownModule():
    pass


class ParserSetupTestCase(TestCase):

    @classmethod
    def setUpClass(self):
        # for fixture in self.fixtures:
        #     management.call_command("loaddata", fixture)

        self.iati_identifier = "NL-KVK-51018586-0666"

        self.iati_105 = build_xml("1.05", self.iati_identifier)

        dummy_source = synchroniser_factory.DatasetFactory.create(filetype=2)

        self.parser_105 = ParseManager(
            dummy_source, self.iati_105).get_parser()

        assert(isinstance(self.parser_105, OrgParse_105))

    @classmethod
    def tearDownClass(self):
        pass


@pytest.mark.skip
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

        self.organisation = iati_factory.OrganisationFactory.create()

        self.parser_105.default_lang = self.organisation.default_lang
        self.parser_105.register_model('Organisation', self.organisation)


    def test_iati_organisations__iati_organisation(self):
        attribs = {
            'default-currency': 'EUR',
            'last-updated-datetime': '2014-09-10T07:15:37Z',
            '{http://www.w3.org/XML/1998/namespace}lang': 'en',
        }

        element = E('iati-organisation',
                    E('iati-identifier', 'test-id', {}), attribs)

        self.parser_105.iati_organisations__iati_organisation(element)

        organisation = self.parser_105.get_model('Organisation')

        self.assertEqual(organisation.organisation_identifier, 'test-id')
        self.assertEqual(organisation.default_currency_id,
                         attribs['default-currency'])
        self.assertEqual(
            organisation.last_updated_datetime,
            self.parser_105.validate_date(
                attribs['last-updated-datetime']))

    def test_iati_organisations__iati_organisation__name(self):
        element = E('name', 'test narrative name')

        self.parser_105.iati_organisations__iati_organisation__name(element)

        narrative = self.parser_105.get_model('OrganisationNameNarrative')

        self.assertEqual('test narrative name', narrative.content)
