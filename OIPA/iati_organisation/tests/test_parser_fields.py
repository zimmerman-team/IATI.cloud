"""
    Unit tests for all fields in the parser, for multiple IATI versions.
"""

import copy
import datetime
import pytest

from django.core import management
from django.test import TestCase as DjangoTestCase
from lxml.builder import E

import iati_codelists.models as codelist_models
from geodata.models import Country
from iati.factory import iati_factory
from iati.parser.parse_manager import ParseManager
from iati_organisation.parser.organisation_2_02 import Parse as OrgParse_202
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

@pytest.fixture(scope='session')
def setUpModule():
    fixtures = ['test_vocabulary', 'test_codelists.json', 'test_geodata.json']

    for fixture in fixtures:
        management.call_command("loaddata", fixture)


def tearDownModule():
    pass


class ParserSetupTestCase(DjangoTestCase):

    @classmethod
    def setUpClass(self):

        self.iati_identifier = "NL-KVK-51018586-0666"
        self.alt_iati_identifier = "NL-KVK-51018586-0667"

        self.iati_202 = build_xml("2.02", self.iati_identifier)
        dummy_source = synchroniser_factory.DatasetFactory.create(
            name="dataset-6", filetype=2)
        self.parser_202 = ParseManager(
            dummy_source, self.iati_202).get_parser()

        assert(isinstance(self.parser_202, OrgParse_202))

    @classmethod
    def tearDownClass(self):
        pass


class OrganisationTestCase(ParserSetupTestCase):
    """
    iati_activities__iati_activity
    CHANGELOG
    2.02: The version attribute was removed.
    1.02: Introduced the linked-data-uri attribute on iati-activity element
    """

    def setUp(self):
        self.iati_202 = copy_xml_tree(self.iati_202)

        self.attrs = {
            "default-currency": "USD",
            "last-updated-datetime": datetime.datetime.now().isoformat(' '),
        }

        # default activity model fields
        self.defaults = {
            "hierarchy": 1,
            "default_lang": "en",
        }

        iati_organisation = E("iati-organisation", **self.attrs)
        iati_organisation.append(
            E("organisation-identifier", self.iati_identifier))

        self.iati_202.append(iati_organisation)
        # ISO 639-1:2002
        self.iati_202.attrib[
            '{http://www.w3.org/XML/1998/namespace}lang'
        ] = "en"

        self.organisation = iati_factory.OrganisationFactory.create()
        self.parser_202.default_lang = self.organisation.default_lang
        self.parser_202.register_model('Organisation', self.organisation)

    def test_iati_organisations__iati_organisation(self):
        attribs = {
            'default-currency': 'EUR',
            'last-updated-datetime': '2014-09-10T07:15:37Z',
            '{http://www.w3.org/XML/1998/namespace}lang': 'en',

        }
        element = E('iati-organisation', E('organisation-identifier',
                                           'AA-AAA-123456789', {}), attribs)

        self.parser_202.iati_organisations__iati_organisation(element)

        org = self.parser_202.get_model('Organisation')
        """:type : org_models.Organisation """
        self.assertEqual(org.organisation_identifier, 'AA-AAA-123456789')
        self.assertEqual(org.default_currency_id, attribs['default-currency'])
        self.assertEqual(
            org.last_updated_datetime,
            self.parser_202.validate_date(
                element.attrib.get('last-updated-datetime')))
        self.assertEqual(org.organisation_identifier, "AA-AAA-123456789")

    def test_iati_organisations__iati_organisation__name(self):
        attribs = {

        }

        element = E('name', attribs)
        self.parser_202.iati_organisations__iati_organisation__name(element)
        """:type : org_models.Organisation """
        attribs = {}
        element = E('narrative', 'test narrative name', attribs)

        self.parser_202.iati_organisations__iati_organisation__name__narrative(
            element)
        model = self.parser_202.get_model('OrganisationNameNarrative')
        self.assertEqual('test narrative name', model.content)

    def test_iati_organisations__iati_organisation__reporting_org(self):
        self.test_iati_organisations__iati_organisation()
        attribs = {
            'ref': 'AA-AAA-123456789',
            'type': '40',
            'secondary-reporter': '0',
        }

        element = E('reporting-org', attribs)

        self.parser_202.iati_organisations__iati_organisation__reporting_org(
            element)
        model = self.parser_202.get_model('OrganisationReportingOrganisation')

        self.assertEqual(model.reporting_org_identifier, 'AA-AAA-123456789')
        self.assertEqual(model.org_type_id, '40')
        self.assertEqual(model.secondary_reporter, False)

    def test_iati_organisations__iati_organisation__reporting_org__narrative(self):  # NOQA: E501
        self.test_iati_organisations__iati_organisation__reporting_org()

        attribs = {

        }
        element = E('narrative', 'test narrative text', attribs)

        self.parser_202.iati_organisations__iati_organisation__reporting_org__narrative(  # NOQA: E501
            element)
        model = self.parser_202.get_model(
            'OrganisationReportingOrganisationNarrative')
        self.assertEqual('test narrative text', model.content)

    # def test_iati_organisations__iati_organisation__total_budget(self):
        # self.test_iati_organisations__iati_organisation()
        # attr = {
        # 'status': '1'
        # }
        # element = E('total-budget', attr)

        # self.parser_202.iati_organisations__iati_organisation__total_budget(
        # element)
        # model = self.parser_202.get_model('TotalBudget')
        # self.assertEqual(model.status.code, attr['status'])

    def test_iati_organisations__iati_organisation__total_budget(self):
        self.test_iati_organisations__iati_organisation()
        attr = {}
        element = E('total-budget', attr)

        self.parser_202.iati_organisations__iati_organisation__total_budget(
            element)
        model = self.parser_202.get_model('TotalBudget')
        self.assertEqual(model.status.code, '1')

    def test_iati_organisations__iati_organisation__total_budget__period_start(
            self):
        self.test_iati_organisations__iati_organisation__total_budget()
        attribs = {
            'iso-date': '2014-01-01',

        }
        element = E('period-start', attribs)
        self.parser_202.iati_organisations__iati_organisation__total_budget__period_start(  # NOQA: E501
            element)
        model = self.parser_202.get_model('TotalBudget')
        """:type : org_models.TotalBudget """
        self.assertEqual(model.period_start,
                         self.parser_202.validate_date('2014-01-01'))

    def test_iati_organisations__iati_organisation__total_budget__period_end(
            self):
        self.test_iati_organisations__iati_organisation__total_budget()
        attribs = {
            'iso-date': '2014-12-31',

        }
        element = E('period-end', attribs)
        self.parser_202.iati_organisations__iati_organisation__total_budget__period_end(  # NOQA: E501
            element)
        model = self.parser_202.get_model('TotalBudget')
        """:type : org_models.TotalBudget """
        self.assertEqual(model.period_end,
                         self.parser_202.validate_date('2014-12-31'))

    def test_iati_organisations__iati_organisation__total_budget__value(self):
        """attributes:
            'currency':'USD',
        'value-date':'2014-01-01',

        tag:value
        """
        self.test_iati_organisations__iati_organisation__total_budget()
        attribs = {
            'currency': 'USD',
            'value-date': '2014-01-01',

        }
        element = E('value', '123', attribs)
        self.parser_202.iati_organisations__iati_organisation__total_budget__value(  # NOQA: E501
            element)
        model = self.parser_202.get_model('TotalBudget')
        """:type : org_models.TotalBudget """
        self.assertEqual(
            model.currency, self.parser_202.get_or_none(
                codelist_models.Currency, code=(
                    element.attrib.get('currency'))))
        self.assertEqual(model.value, '123')
        self.assertEqual(model.value_date,
                         self.parser_202.validate_date('2014-01-01'))

    def test_iati_organisations__iati_organisation__total_budget__budget_line(
            self):
        """attributes:
            'ref':'1234',

    tag:budget-line
    """
        self.test_iati_organisations__iati_organisation__total_budget()

        attribs = {
            'ref': '1234',

        }
        element = E('budget-line', attribs)

        self.parser_202.iati_organisations__iati_organisation__total_budget__budget_line(  # NOQA: E501
            element)
        model = self.parser_202.get_model('TotalBudgetLine')
        """ :type : org_models.BudgetLine """
        self.assertEqual(model.ref, '1234')
        attribs = {

        }
        element = E('narrative', 'test narrative text', attribs)
        self.parser_202.iati_organisations__iati_organisation__total_budget__budget_line__narrative(  # NOQA: E501
            element)
        model = self.parser_202.get_model('TotalBudgetLineNarrative')
        self.assertEqual('test narrative text', model.content)

    def test_iati_organisations__iati_organisation__total_budget__budget_line__value(self):  # NOQA: E501
        """attributes:
            'currency':'USD',
        'value-date':'2014-01-01',

        tag:value
        """
        self\
            .test_iati_organisations__iati_organisation__total_budget__budget_line()  # NOQA: E501
        attribs = {
            'currency': 'USD',
            'value-date': '2014-01-01',

        }
        element = E('value', '1234', attribs)
        self\
            .parser_202.iati_organisations__iati_organisation__total_budget__budget_line__value(  # NOQA: E501
                element
            )
        model = self.parser_202.get_model('TotalBudgetLine')
        """ :type : org_models.BudgetLine """
        self.assertEqual(
            model.currency, self.parser_202.get_or_none(
                codelist_models.Currency, code=(
                    element.attrib.get('currency'))))
        self.assertEqual(
            model.value_date,
            self.parser_202.validate_date(
                element.attrib.get('value-date')))

    def test_iati_organisations__iati_organisation__recipient_org_budget(self):
        """attributes:

        tag:recipient-org-budget
        """
        self.test_iati_organisations__iati_organisation()
        attr = {
            'status': '1'
        }
        element = E('recipient-org-budget', attr)
        self.parser_202.iati_organisations__iati_organisation__recipient_org_budget(  # NOQA: E501
            element)
        model = self.parser_202.get_model('RecipientOrgBudget')
        self.assertEqual(model.status.code, attr['status'])

    def test_iati_organisations__iati_organisation__recipient_org_budget__recipient_org(self):  # NOQA: E501
        """
        attributes:
            'ref':'AA-ABC-1234567',

        tag:recipient-org
        """
        self.test_iati_organisations__iati_organisation__recipient_org_budget()
        attribs = {
            'ref': 'AA-ABC-1234567',

        }
        element = E('recipient-org', attribs)

        self.parser_202.iati_organisations__iati_organisation__recipient_org_budget__recipient_org(  # NOQA: E501
            element)
        model = self.parser_202.get_model('RecipientOrgBudget')
        """ :type : org_models.RecipientOrgBudget """
        self.assertEqual(model.recipient_org_identifier, 'AA-ABC-1234567')

    def test_iati_organisations__iati_organisation__recipient_org_budget__recipient_org__narrative(  # NOQA: E501
            self):
        """attributes:

        tag:narrative
        """
        self\
            .test_iati_organisations__iati_organisation__recipient_org_budget__recipient_org()  # NOQA: E501

        attribs = {

        }
        element = E('narrative', 'test text', attribs)

        self.parser_202\
            .iati_organisations__iati_organisation__recipient_org_budget__recipient_org__narrative(  # NOQA: E501
                element)
        model = self.parser_202.get_model('RecipientOrgBudgetNarrative')
        self.assertEqual(model.content, 'test text')

    def test_iati_organisations__iati_organisation__recipient_org_budget__period_start(self):  # NOQA: E501
        """attributes:
            'iso-date':'2014-01-01',

        tag:period-start
        """
        self.test_iati_organisations__iati_organisation__recipient_org_budget()
        attribs = {
            'iso-date': '2014-01-01',

        }
        element = E('period-start', attribs)
        self.parser_202.iati_organisations__iati_organisation__recipient_org_budget__period_start(  # NOQA: E501
            element)
        model = self.parser_202.get_model('RecipientOrgBudget')
        """ :type : org_models.RecipientOrgBudget """
        self.assertEqual(model.period_start,
                         self.parser_202.validate_date('2014-01-01'))

    def test_iati_organisations__iati_organisation__recipient_org_budget__period_end(self):  # NOQA: E501
        """attributes:
            'iso-date':'2014-12-31',

        tag:period-end
        """
        self.test_iati_organisations__iati_organisation__recipient_org_budget()  # NOQA: E501
        attribs = {
            'iso-date': '2014-12-31',

        }
        element = E('period-end', attribs)
        self.parser_202\
            .iati_organisations__iati_organisation__recipient_org_budget__period_end(  # NOQA: E501
                element)
        model = self.parser_202.get_model('RecipientOrgBudget')
        """ :type : org_models.RecipientOrgBudget """
        self.assertEqual(model.period_end,
                         self.parser_202.validate_date('2014-12-31'))

    def test_iati_organisations__iati_organisation__recipient_org_budget__value(self):  # NOQA: E501
        """attributes:
            'currency':'USD',
        'value-date':'2014-01-01',

        tag:value
        """
        self.test_iati_organisations__iati_organisation__recipient_org_budget()
        attribs = {
            'currency': 'USD',
            'value-date': '2014-01-01',

        }
        element = E('value', '1234', attribs)

        self.parser_202\
            .iati_organisations__iati_organisation__recipient_org_budget__value(  # NOQA: E501
                element)
        model = self.parser_202.get_model('RecipientOrgBudget')
        """ :type : org_models.RecipientOrgBudget """
        self.assertEqual(
            model.currency, self.parser_202.get_or_none(
                codelist_models.Currency, code=(
                    element.attrib.get('currency'))))
        self.assertEqual(model.value, '1234')

    def test_iati_organisations__iati_organisation__recipient_org_budget__budget_line(self):  # NOQA: E501
        """attributes:
            'ref':'1234',

        tag:budget-line
        """
        self.test_iati_organisations__iati_organisation__recipient_org_budget()
        attribs = {
            'ref': '1234',

        }
        element = E('budget-line', attribs)

        self.parser_202\
            .iati_organisations__iati_organisation__recipient_org_budget__budget_line(  # NOQA: E501
                element)
        model = self.parser_202.get_model('RecipientOrgBudgetLine')
        """ :type : org_models.BudgetLine """
        self.assertEqual(model.ref, '1234')

    def test_iati_organisations__iati_organisation__recipient_org_budget__budget_line__value(self):  # NOQA: E501
        """attributes:
            'currency':'USD',
        'value-date':'2014-01-01',

        tag:value
        """
        self\
            .test_iati_organisations__iati_organisation__recipient_org_budget__budget_line()  # NOQA: E501
        attribs = {
            'currency': 'USD',
            'value-date': '2014-01-01',

        }
        element = E('value', '1234', attribs)

        self.parser_202.iati_organisations__iati_organisation__recipient_org_budget__budget_line__value(  # NOQA: E501
            element)
        model = self.parser_202.get_model('RecipientOrgBudgetLine')
        self.assertEqual(
            model.currency, self.parser_202.get_or_none(
                codelist_models.Currency, code=(
                    element.attrib.get('currency'))))
        self.assertEqual(model.value, '1234')

    def test_iati_organisations__iati_organisation__recipient_org_budget__budget_line__narrative(  # NOQA: E501
            self):
        """attributes:

        tag:narrative
        """
        self.test_iati_organisations__iati_organisation__recipient_org_budget__budget_line()  # NOQA: E501
        attribs = {

        }
        element = E('narrative', 'test text', attribs)
        self.parser_202.iati_organisations__iati_organisation__recipient_org_budget__budget_line__narrative(  # NOQA: E501
            element)
        model = self.parser_202.get_model('RecipientOrgBudgetLineNarrative')
        self.assertEqual('test text', model.content)

    def test_iati_organisations__iati_organisation__recipient_country_budget(self):  # NOQA: E501
        """attributes:

        tag:recipient-country-budget
        """
        self.test_iati_organisations__iati_organisation()
        attribs = {

        }
        element = E('recipient-country-budget', attribs)
        self.parser_202\
            .iati_organisations__iati_organisation__recipient_country_budget(
                element)
        self.parser_202.get_model('RecipientCountryBudget')

    def test_iati_organisations__iati_organisation__recipient_country_budget__recipient_country(  # NOQA: E501
            self):
        """attributes:
            'code':'AF',

        tag:recipient-country
        """
        self.test_iati_organisations__iati_organisation__recipient_country_budget()  # NOQA: E501
        attribs = {
            'code': 'AF',

        }
        element = E('recipient-country', attribs)

        self.parser_202.iati_organisations__iati_organisation__recipient_country_budget__recipient_country(  # NOQA: E501
            element)
        model = self.parser_202.get_model('RecipientCountryBudget')
        """ :type : org_models.RecipientCountryBudget """
        self.assertEqual(
            model.country,
            self.parser_202.get_or_none(
                Country,
                code=element.attrib.get('code')))
        # assert

    def test_iati_organisations__iati_organisation__recipient_country_budget__period_start(self):  # NOQA: E501
        """attributes:
            'iso-date':'2014-01-01',

        tag:period-start
        """
        self\
            .test_iati_organisations__iati_organisation__recipient_country_budget()  # NOQA: E501
        attribs = {
            'iso-date': '2014-01-01',

        }
        element = E('period-start', attribs)

        self.parser_202.iati_organisations__iati_organisation__recipient_country_budget__period_start(  # NOQA: E501
            element)
        model = self.parser_202.get_model('RecipientCountryBudget')
        self.assertEqual(model.period_start,
                         self.parser_202.validate_date('2014-01-01'))

    def test_iati_organisations__iati_organisation__recipient_country_budget__period_end(self):  # NOQA: E501
        """attributes:
            'iso-date':'2014-12-31',

        tag:period-end
        """
        self\
            .test_iati_organisations__iati_organisation__recipient_country_budget()  # NOQA: E501
        attribs = {
            'iso-date': '2014-12-31',

        }
        element = E('period-end', attribs)
        self.parser_202.iati_organisations__iati_organisation__recipient_country_budget__period_end(  # NOQA: E501
            element)
        model = self.parser_202.get_model('RecipientCountryBudget')
        self.assertEqual(model.period_end,
                         self.parser_202.validate_date('2014-12-31'))

    def test_iati_organisations__iati_organisation__recipient_country_budget__value(self):  # NOQA: E501
        """attributes:
            'currency':'USD',
        'value-date':'2014-01-01',

        tag:value
        """
        self\
            .test_iati_organisations__iati_organisation__recipient_country_budget()  # NOQA: E501
        attribs = {
            'currency': 'USD',
            'value-date': '2014-01-01',

        }
        element = E('value', '1234', attribs)
        self.parser_202.iati_organisations__iati_organisation__recipient_country_budget__value(  # NOQA: E501
            element)
        model = self.parser_202.get_model('RecipientCountryBudget')
        self.assertEqual(
            model.currency, self.parser_202.get_or_none(
                codelist_models.Currency, code=(
                    element.attrib.get('currency'))))
        self.assertEqual(model.value, '1234')
        # assert

    def test_iati_organisations__iati_organisation__recipient_country_budget__budget_line(self):  # NOQA: E501
        """attributes:
            'ref':'1234',

        tag:budget-line
        """
        self.test_iati_organisations__iati_organisation__recipient_country_budget()  # NOQA: E501
        attribs = {
            'ref': '1234',

        }
        element = E('budget-line', attribs)
        self.parser_202.iati_organisations__iati_organisation__recipient_country_budget__budget_line(  # NOQA: E501
            element)
        model = self.parser_202.get_model('RecipientCountryBudgetLine')
        """ :type : org_models.BudgetLine """
        self.assertEqual(model.ref, '1234')

    def test_iati_organisations__iati_organisation__recipient_country_budget__budget_line__value(  # NOQA: E501
            self):
        """attributes:
            'currency':'USD',
        'value-date':'2014-01-01',

        tag:value
        """
        self.test_iati_organisations__iati_organisation__recipient_country_budget__budget_line()  # NOQA: E501
        attribs = {
            'currency': 'USD',
            'value-date': '2014-01-01',

        }
        element = E('value', '1234', attribs)
        model = self.parser_202.get_model('Organisation')
        self.parser_202.iati_organisations__iati_organisation__recipient_country_budget__budget_line__value(  # NOQA: E501
            element)
        model = self.parser_202.get_model('RecipientCountryBudgetLine')
        self.assertEqual(
            model.currency, self.parser_202.get_or_none(
                codelist_models.Currency, code=(
                    element.attrib.get('currency'))))
        self.assertEqual(model.value, '1234')
        # assert

    def test_iati_organisations__iati_organisation__recipient_country_budget__budget_line__narrative(  # NOQA: E501
            self):
        """attributes:

        tag:narrative
        """
        self.test_iati_organisations__iati_organisation__recipient_country_budget__budget_line()  # NOQA: E501
        attribs = {

        }
        element = E('narrative', 'test text', attribs)
        self.parser_202.iati_organisations__iati_organisation__recipient_country_budget__budget_line__narrative(  # NOQA: E501
            element)
        model = self.parser_202.get_model(
            'RecipientCountryBudgetLineNarrative')
        self.assertEqual('test text', model.content)

    def test_iati_organisations__iati_organisation__recipient_region_budget(self):  # NOQA: E501
        """attributes:

        tag:recipient-region-budget
        """
        self.test_iati_organisations__iati_organisation()
        attribs = {

        }
        element = E('recipient-region-budget', attribs)
        self.parser_202\
            .iati_organisations__iati_organisation__recipient_region_budget(
                element
            )
        self.parser_202.get_model('RecipientRegionBudget')

    def test_iati_organisations__iati_organisation__recipient_region_budget__recipient_region(  # NOQA: E501
            self):
        """attributes:
            'code':'AF',

        tag:recipient-region
        """
        self\
            .test_iati_organisations__iati_organisation__recipient_region_budget()  # NOQA: E501
        attr = {
            'code': '998',
            'vocabulary': '1',
            'vocabulary-uri': "http://example.com/vocab.html"
        }

        element = E('recipient-region', attr)
        self.parser_202\
            .iati_organisations__iati_organisation__recipient_region_budget__recipient_region(  # NOQA: E501
                element)
        model = self.parser_202.get_model('RecipientRegionBudget')

        self.assertEqual(model.region.code, attr['code'])
        self.assertEqual(model.vocabulary.code, attr['vocabulary'])
        self.assertEqual(model.vocabulary_uri, attr['vocabulary-uri'])

    def test_iati_organisations__iati_organisation__recipient_region_budget__period_start(self):  # NOQA: E501
        """attributes:
            'iso-date':'2014-01-01',

        tag:period-start
        """
        self\
            .test_iati_organisations__iati_organisation__recipient_region_budget()  # NOQA: E501
        attribs = {
            'iso-date': '2014-01-01',

        }
        element = E('period-start', attribs)

        self.parser_202\
            .iati_organisations__iati_organisation__recipient_region_budget__period_start(  # NOQA: E501
                element
            )
        model = self.parser_202.get_model('RecipientRegionBudget')
        self.assertEqual(model.period_start,
                         self.parser_202.validate_date('2014-01-01'))

    def test_iati_organisations__iati_organisation__recipient_region_budget__period_end(self):  # NOQA: E501
        """attributes:
            'iso-date':'2014-12-31',

        tag:period-end
        """
        self.test_iati_organisations__iati_organisation__recipient_region_budget()  # NOQA: E501
        attribs = {
            'iso-date': '2014-12-31',

        }
        element = E('period-end', attribs)
        self.parser_202.iati_organisations__iati_organisation__recipient_region_budget__period_end(  # NOQA: E501
            element)
        model = self.parser_202.get_model('RecipientRegionBudget')
        self.assertEqual(model.period_end,
                         self.parser_202.validate_date('2014-12-31'))

    def test_iati_organisations__iati_organisation__recipient_region_budget__value(self):  # NOQA: E501
        """attributes:
            'currency':'USD',
        'value-date':'2014-01-01',

        tag:value
        """
        self\
            .test_iati_organisations__iati_organisation__recipient_region_budget()  # NOQA: E501
        attribs = {
            'currency': 'USD',
            'value-date': '2014-01-01',

        }
        element = E('value', '1234', attribs)
        self\
            .parser_202.iati_organisations__iati_organisation__recipient_region_budget__value(  # NOQA: E501
                element)
        model = self.parser_202.get_model('RecipientRegionBudget')
        self.assertEqual(
            model.currency, self.parser_202.get_or_none(
                codelist_models.Currency, code=(
                    element.attrib.get('currency'))))
        self.assertEqual(model.value, '1234')
        # assert

    def test_iati_organisations__iati_organisation__recipient_region_budget__budget_line(self):  # NOQA: E501
        """attributes:
            'ref':'1234',

        tag:budget-line
        """
        self\
            .test_iati_organisations__iati_organisation__recipient_region_budget()  # NOQA: E501
        attribs = {
            'ref': '1234',

        }
        element = E('budget-line', attribs)
        self\
            .parser_202.iati_organisations__iati_organisation__recipient_region_budget__budget_line(  # NOQA: E501
                element)
        model = self.parser_202.get_model('RecipientRegionBudgetLine')
        """ :type : org_models.BudgetLine """
        self.assertEqual(model.ref, '1234')

    def test_iati_organisations__iati_organisation__recipient_region_budget__budget_line__value(  # NOQA: E501
            self):
        """attributes:
            'currency':'USD',
        'value-date':'2014-01-01',

        tag:value
        """
        self\
            .test_iati_organisations__iati_organisation__recipient_region_budget__budget_line()  # NOQA: E501
        attribs = {
            'currency': 'USD',
            'value-date': '2014-01-01',

        }
        element = E('value', '1234', attribs)
        model = self.parser_202.get_model('Organisation')
        self.parser_202\
            .iati_organisations__iati_organisation__recipient_region_budget__budget_line__value(  # NOQA: E501
                element)
        model = self.parser_202.get_model('RecipientRegionBudgetLine')
        self.assertEqual(
            model.currency, self.parser_202.get_or_none(
                codelist_models.Currency, code=(
                    element.attrib.get('currency'))))
        self.assertEqual(model.value, '1234')
        # assert

    def test_iati_organisations__iati_organisation__recipient_region_budget__budget_line__narrative(  # NOQA: E501
            self):
        """attributes:

        tag:narrative
        """
        self\
            .test_iati_organisations__iati_organisation__recipient_region_budget__budget_line()  # NOQA: E501
        attribs = {

        }
        element = E('narrative', 'test text', attribs)
        self\
            .parser_202.iati_organisations__iati_organisation__recipient_region_budget__budget_line__narrative(  # NOQA: E501
                element)
        model = self.parser_202.get_model('RecipientRegionBudgetLineNarrative')
        self.assertEqual('test text', model.content)

    def test_iati_organisations__iati_organisation__total_expenditure(self):
        """attributes:

        tag:recipient-country-budget
        """
        self.test_iati_organisations__iati_organisation()
        attrs = {}
        element = E('total-expenditure', attrs)
        self.parser_202\
            .iati_organisations__iati_organisation__total_expenditure(
                element)
        self.parser_202.get_model('TotalExpenditure')

    def test_iati_organisations__iati_organisation__total_expenditure__period_start(self):  # NOQA: E501
        """attributes:
            'iso-date':'2014-01-01',

        tag:period-start
        """
        self.test_iati_organisations__iati_organisation__total_expenditure()
        attrs = {
            'iso-date': datetime.datetime.now().isoformat(' '),
        }
        element = E('period-start', attrs)

        self.parser_202\
            .iati_organisations__iati_organisation__total_expenditure__period_start(  # NOQA: E501
                element)
        model = self.parser_202.get_model('TotalExpenditure')
        self.assertEqual(str(model.period_start), attrs['iso-date'])

    def test_iati_organisations__iati_organisation__total_expenditure__period_end(self):  # NOQA: E501
        """attributes:
            'iso-date':'2014-12-31',
            tag:period-end
        """
        self.test_iati_organisations__iati_organisation__total_expenditure()
        attrs = {
            'iso-date': datetime.datetime.now().isoformat(' '),
        }
        element = E('period-end', attrs)

        self.parser_202\
            .iati_organisations__iati_organisation__total_expenditure__period_end(  # NOQA: E501
                element)
        model = self.parser_202.get_model('TotalExpenditure')
        self.assertEqual(str(model.period_end), attrs['iso-date'])

    def test_iati_organisations__iati_organisation__total_expenditure__value(self):  # NOQA: E501
        """attributes:
            'currency':'USD',
            'value-date':'2014-01-01',

            tag:value
        """
        self.test_iati_organisations__iati_organisation__total_expenditure()
        attrs = {
            'currency': 'USD',
            'value-date': datetime.datetime.now().isoformat(' '),
        }
        element = E('value', '1234', attrs)
        self.parser_202\
            .iati_organisations__iati_organisation__total_expenditure__value(
                element)
        model = self.parser_202.get_model('TotalExpenditure')
        self.assertEqual(model.currency.code, attrs['currency'])
        self.assertEqual(model.value, '1234')
        self.assertEqual(str(model.value_date), attrs['value-date'])

    def test_iati_organisations__iati_organisation__total_expenditure__expense_line(self):  # NOQA: E501
        """attributes:
            'ref':'1234',

        tag:budget-line
        """
        self.test_iati_organisations__iati_organisation__total_expenditure()
        attrs = {
            'ref': '1234',
        }
        element = E('expense-line', attrs)
        self.parser_202\
            .iati_organisations__iati_organisation__total_expenditure__expense_line(  # NOQA: E501
                element)
        model = self.parser_202.get_model('TotalExpenditureBudgetLine')
        self.assertEqual(model.ref, '1234')

    def test_iati_organisations__iati_organisation__total_expenditure__expense_line__value(self):  # NOQA: E501
        """attributes:
            'currency':'USD',
        'value-date':'2014-01-01',

        tag:value
        """
        self\
            .test_iati_organisations__iati_organisation__total_expenditure__expense_line()  # NOQA: E501
        attrs = {
            'currency': 'USD',
            'value-date': datetime.datetime.now().isoformat(' '),
        }
        element = E('value', '1234', attrs)

        self.parser_202\
            .iati_organisations__iati_organisation__total_expenditure__expense_line__value(  # NOQA: E501
                element)

        model = self.parser_202.get_model('TotalExpenditureBudgetLine')

        self.assertEqual(model.currency.code, attrs.get('currency'))
        self.assertEqual(model.value, '1234')
        self.assertEqual(str(model.value_date), attrs['value-date'])

    def test_iati_organisations__iati_organisation__total_expenditure__expense_line__narrative(  # NOQA: E501
            self):
        """attributes:

        tag:narrative
        """
        self\
            .test_iati_organisations__iati_organisation__total_expenditure__expense_line()  # NOQA: E501

        attrs = {

        }
        element = E('narrative', 'test text', attrs)
        self.parser_202\
            .iati_organisations__iati_organisation__total_expenditure__expense_line__narrative(  # NOQA: E501
                element)
        model = self.parser_202.get_model('TotalExpenditureLineNarrative')
        self.assertEqual(model.content, 'test text')

    def test_iati_organisations__iati_organisation__document_link(self):
        """attributes:
            'format':'application/vnd.oasis.opendocument.text',
        'url':'http:www.example.org/docs/report_en.odt',

        tag:document-link
        """
        self.test_iati_organisations__iati_organisation()
        attribs = {
            'format': 'application/vnd.oasis.opendocument.text',
            'url': 'http:www.example.org/docs/report_en.odt',

        }
        element = E('document-link', attribs)
        self.parser_202.iati_organisations__iati_organisation__document_link(
            element)
        model = self.parser_202.get_model('OrganisationDocumentLink')
        """ :type : org_models.OrganisationDocumentLink """
        self.assertEqual(model.url, element.attrib.get('url'))
        self.assertEqual(
            model.file_format,
            self.parser_202.get_or_none(
                codelist_models.FileFormat,
                code=element.attrib.get('format')))

    def test_iati_organisations__iati_organisation__document_link__title(self):
        self.test_iati_organisations__iati_organisation__document_link()
        attribs = {

        }
        element = E('title', attribs)
        self.parser_202\
            .iati_organisations__iati_organisation__document_link__title(
                element)

    def test_iati_organisations__iati_organisation__document_link__title__narrative(self):  # NOQA: E501
        """attributes:

        tag:narrative
        """
        self.test_iati_organisations__iati_organisation__document_link__title()
        attribs = {

        }
        element = E('narrative', 'test text', attribs)
        self.parser_202\
            .iati_organisations__iati_organisation__document_link__title__narrative(  # NOQA: E501
                element)
        model = self.parser_202.get_model('DocumentLinkTitleNarrative')
        self.assertEqual('test text', model.content)

    def test_iati_organisations__iati_organisation__document_link__category(
            self):
        """attributes:
            'code':'B01',

        tag:category
        """
        self.test_iati_organisations__iati_organisation__document_link()
        attribs = {
            'code': 'B01',

        }
        element = E('category', attribs)

        model = self.parser_202.get_model('OrganisationDocumentLink')
        model.organisation.save()
        model.organisation = model.organisation
        model.save()

        self\
            .parser_202.iati_organisations__iati_organisation__document_link__category(  # NOQA: E501
                element)
        model = self.parser_202.get_model('OrganisationDocumentLink')

    def test_iati_organisations__iati_organisation__document_link__language(
            self):
        """attributes:
            'code':'en',

        tag:language
        """
        self.test_iati_organisations__iati_organisation__document_link()
        attribs = {
            'code': 'en',

        }
        element = E('language', attribs)

        self\
            .parser_202.iati_organisations__iati_organisation__document_link__language(  # NOQA: E501
                element)
        model = self.parser_202.get_model('OrganisationDocumentLink')
        """ :type : org_models.OrganisationDocumentLink """
        self.assertEqual(
            model.language,
            self.parser_202.get_or_none(
                codelist_models.Language,
                code=element.attrib.get('code')))

    def test_iati_organisations__iati_organisation__document_link_document_date_202(self):  # NOQA: E501
        """
        """
        attrs = {
            'iso-date': datetime.datetime.now().isoformat(' ')
        }

        document_date = E('document-date', **attrs)

        self.test_iati_organisations__iati_organisation__document_link()

        self.parser_202\
            .iati_organisations__iati_organisation__document_link__document_date(  # NOQA: E501
                document_date)
        document_link = self.parser_202.get_model('OrganisationDocumentLink')

        self.assertEqual(str(document_link.iso_date), attrs['iso-date'])

    def test_iati_organisations__iati_organisation__document_link__recipient_country(self):  # NOQA: E501
        """attributes:
            'code':'AF',

        tag:recipient-country
        """
        self.test_iati_organisations__iati_organisation__document_link()
        model = self.parser_202.get_model('OrganisationDocumentLink')
        model.organisation.save()
        model.organisation = model.organisation
        model.save()
        attribs = {
            'code': 'AF',

        }
        element = E('recipient-country', attribs)

        self.parser_202\
            .iati_organisations__iati_organisation__document_link__recipient_country(  # NOQA: E501
                element)
