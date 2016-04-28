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

from iati.parser.parse_manager import ParseManager

from iati_synchroniser.models import IatiXmlSource, Publisher
import iati.models as iati_models
import iati_codelists.models as codelist_models
import iati_organisation.models as org_models
from geodata.models import Country
from iati.factory import iati_factory

from iati.parser.IATI_2_01 import Parse as Parser_201
from iati_organisation.parser.organisation_2_01 import Parse as OrgParse_201


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

def setUpModule():
    fixtures = ['test_publisher.json', 'test_codelists.json', 'test_vocabulary', 'test_geodata.json']

    for fixture in fixtures:
        management.call_command("loaddata", fixture)

def tearDownModule():
    management.call_command('flush', interactive=False, verbosity=0)


class ParserSetupTestCase(DjangoTestCase):

    @classmethod
    def setUpClass(self):

        self.iati_identifier = "NL-KVK-51018586-0666"
        self.alt_iati_identifier = "NL-KVK-51018586-0667"

        self.iati_201 = build_xml("2.01", self.iati_identifier)
        dummy_source = IatiXmlSource.objects.get(id=2)
        self.parser_201 = ParseManager(dummy_source, self.iati_201).get_parser()

        assert(isinstance(self.parser_201, OrgParse_201))

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
        self.iati_201 = copy_xml_tree(self.iati_201)

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
        iati_organisation.append(E("organisation-identifier", self.iati_identifier))

        self.iati_201.append(iati_organisation)
        self.iati_201.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en" # ISO 639-1:2002


        self.organisation = iati_factory.OrganisationFactory.create()
        self.parser_201.default_lang = "en"
        self.parser_201.register_model('Organisation', self.organisation)

    def test_iati_organisations__iati_organisation(self):
        attribs = {
                'default-currency':'EUR',
                'last-updated-datetime':'2014-09-10T07:15:37Z',
                '{http://www.w3.org/XML/1998/namespace}lang':'en',

                }
        element = E('iati-organisation',E('organisation-identifier','AA-AAA-123456789',{}),attribs)

        self.parser_201.iati_organisations__iati_organisation(element)

        org = self.parser_201.get_model('Organisation')
        """:type : org_models.Organisation """
        self.assertEqual(org.id,'AA-AAA-123456789')
        self.assertEqual(org.default_currency_id , attribs['default-currency'])
        self.assertEqual(org.last_updated_datetime,self.parser_201.validate_date(element.attrib.get('last-updated-datetime')))
        self.assertEqual(org.id,"AA-AAA-123456789")


    def test_iati_organisations__iati_organisation__name(self):
        attribs = {

        }

        element = E('name',attribs)
        self.parser_201.iati_organisations__iati_organisation__name(element)
        org = self.parser_201.get_model('Organisation')
        """:type : org_models.Organisation """
        attribs = {

        }
        element = E('narrative','test narrative name',attribs)

        self.parser_201.iati_organisations__iati_organisation__name__narrative(element)
        model = self.parser_201.get_model('OrganisationNameNarrative')
        self.assertEqual('test narrative name',model.content)


    def test_iati_organisations__iati_organisation__reporting_org(self):
        self.test_iati_organisations__iati_organisation()
        attribs = {
            'ref':'AA-AAA-123456789',
            'type':'40',
            'secondary-reporter':'0',
        }

        element = E('reporting-org',attribs)

        self.parser_201.iati_organisations__iati_organisation__reporting_org(element)
        model = self.parser_201.get_model('OrganisationReportingOrganisation')

        self.assertEqual(model.reporting_org_identifier, 'AA-AAA-123456789')
        self.assertEqual(model.org_type_id,'40')
        self.assertEqual(model.secondary_reporter,False)


    def test_iati_organisations__iati_organisation__reporting_org__narrative(self):
        self.test_iati_organisations__iati_organisation__reporting_org()

        attribs = {

        }
        element = E('narrative','test narrative text',attribs)

        self.parser_201.iati_organisations__iati_organisation__reporting_org__narrative(element)
        model = self.parser_201.get_model('OrganisationReportingOrganisationNarrative')
        self.assertEqual('test narrative text',model.content)
        #assert


    def test_iati_organisations__iati_organisation__total_budget(self):
        self.test_iati_organisations__iati_organisation()
        attribs = {

        }
        element = E('total-budget',attribs)

        self.parser_201.iati_organisations__iati_organisation__total_budget(element)
        model = self.parser_201.get_model('TotalBudget')


    def test_iati_organisations__iati_organisation__total_budget__period_start(self):
        self.test_iati_organisations__iati_organisation__total_budget()
        attribs = {
                'iso-date':'2014-01-01',

        }
        element = E('period-start',attribs)
        self.parser_201.iati_organisations__iati_organisation__total_budget__period_start(element)
        model = self.parser_201.get_model('TotalBudget')
        """:type : org_models.TotalBudget """
        self.assertEqual(model.period_start,self.parser_201.validate_date('2014-01-01'))
        #assert


    def test_iati_organisations__iati_organisation__total_budget__period_end(self):
        self.test_iati_organisations__iati_organisation__total_budget()
        attribs = {
                'iso-date':'2014-12-31',

        }
        element = E('period-end',attribs)
        self.parser_201.iati_organisations__iati_organisation__total_budget__period_end(element)
        model = self.parser_201.get_model('TotalBudget')
        """:type : org_models.TotalBudget """
        self.assertEqual(model.period_end,self.parser_201.validate_date('2014-12-31'))
        #assert




    '''attributes:
            'currency':'USD',
        'value-date':'2014-01-01',

    tag:value
    '''
    def test_iati_organisations__iati_organisation__total_budget__value(self):
        self.test_iati_organisations__iati_organisation__total_budget()
        attribs = {
                'currency':'USD',
        'value-date':'2014-01-01',

        }
        element = E('value','123',attribs)
        self.parser_201.iati_organisations__iati_organisation__total_budget__value(element)
        model = self.parser_201.get_model('TotalBudget')
        """:type : org_models.TotalBudget """
        self.assertEqual(model.currency,self.parser_201.get_or_none(codelist_models.Currency, code=(element.attrib.get('currency'))))
        self.assertEqual(model.value,'123')
        self.assertEqual(model.value_date,self.parser_201.validate_date('2014-01-01'))

        #assert




    '''attributes:
            'ref':'1234',

    tag:budget-line
    '''
    def test_iati_organisations__iati_organisation__total_budget__budget_line(self):
        self.test_iati_organisations__iati_organisation__total_budget()

        attribs = {
                'ref':'1234',

        }
        element = E('budget-line',attribs)

        self.parser_201.iati_organisations__iati_organisation__total_budget__budget_line(element)
        model = self.parser_201.get_model('TotalBudgetLine')
        """ :type : org_models.BudgetLine """
        self.assertEqual(model.ref,'1234')
        attribs = {

        }
        element = E('narrative','test narrative text',attribs)
        self.parser_201.iati_organisations__iati_organisation__total_budget__budget_line__narrative(element)
        model = self.parser_201.get_model('BudgetLineNarrative')
        self.assertEqual('test narrative text',model.content)
        #assert
        #assert




    '''attributes:
            'currency':'USD',
        'value-date':'2014-01-01',

    tag:value
    '''
    def test_iati_organisations__iati_organisation__total_budget__budget_line__value(self):
        self.test_iati_organisations__iati_organisation__total_budget__budget_line()
        attribs = {
                'currency':'USD',
        'value-date':'2014-01-01',

        }
        element = E('value','1234',attribs)
        self.parser_201.iati_organisations__iati_organisation__total_budget__budget_line__value(element)
        model = self.parser_201.get_model('TotalBudgetLine')
        """ :type : org_models.BudgetLine """
        self.assertEqual(model.currency,self.parser_201.get_or_none(codelist_models.Currency, code=(element.attrib.get('currency'))))
        self.assertEqual(model.value_date,self.parser_201.validate_date(element.attrib.get('value-date')))
        #assert





    '''attributes:

    tag:recipient-org-budget
    '''
    def test_iati_organisations__iati_organisation__recipient_org_budget(self):
        self.test_iati_organisations__iati_organisation()
        attribs = {

        }
        element = E('recipient-org-budget',attribs)
        self.parser_201.iati_organisations__iati_organisation__recipient_org_budget(element)
        model = self.parser_201.get_model('RecipientOrgBudget')

        #assert




    '''attributes:
            'ref':'AA-ABC-1234567',

    tag:recipient-org
    '''
    def test_iati_organisations__iati_organisation__recipient_org_budget__recipient_org(self):
        self.test_iati_organisations__iati_organisation__recipient_org_budget()
        attribs = {
                'ref':'AA-ABC-1234567',

        }
        element = E('recipient-org',attribs)

        self.parser_201.iati_organisations__iati_organisation__recipient_org_budget__recipient_org(element)
        model = self.parser_201.get_model('RecipientOrgBudget')
        """ :type : org_models.RecipientOrgBudget """
        self.assertEqual(model.recipient_org_identifier,'AA-ABC-1234567')
        #assert




    '''attributes:

    tag:narrative
    '''
    def test_iati_organisations__iati_organisation__recipient_org_budget__recipient_org__narrative(self):
        self.test_iati_organisations__iati_organisation__recipient_org_budget__recipient_org()

        attribs = {

        }
        element = E('narrative','test text',attribs)

        self.parser_201.iati_organisations__iati_organisation__recipient_org_budget__recipient_org__narrative(element)
        model = self.parser_201.get_model('RecipientOrgBudgetNarrative')
        self.assertEqual(model.content,'test text')
        #assert




    '''attributes:
            'iso-date':'2014-01-01',

    tag:period-start
    '''
    def test_iati_organisations__iati_organisation__recipient_org_budget__period_start(self):
        self.test_iati_organisations__iati_organisation__recipient_org_budget()
        attribs = {
                'iso-date':'2014-01-01',

        }
        element = E('period-start',attribs)
        self.parser_201.iati_organisations__iati_organisation__recipient_org_budget__period_start(element)
        model = self.parser_201.get_model('RecipientOrgBudget')
        """ :type : org_models.RecipientOrgBudget """
        self.assertEqual(model.period_start,self.parser_201.validate_date('2014-01-01'))

        #assert




    '''attributes:
            'iso-date':'2014-12-31',

    tag:period-end
    '''
    def test_iati_organisations__iati_organisation__recipient_org_budget__period_end(self):
        self.test_iati_organisations__iati_organisation__recipient_org_budget()
        attribs = {
                'iso-date':'2014-12-31',

        }
        element = E('period-end',attribs)
        self.parser_201.iati_organisations__iati_organisation__recipient_org_budget__period_end(element)
        model = self.parser_201.get_model('RecipientOrgBudget')
        """ :type : org_models.RecipientOrgBudget """
        self.assertEqual(model.period_end,self.parser_201.validate_date('2014-12-31'))





    '''attributes:
            'currency':'USD',
        'value-date':'2014-01-01',

    tag:value
    '''
    def test_iati_organisations__iati_organisation__recipient_org_budget__value(self):
        self.test_iati_organisations__iati_organisation__recipient_org_budget()
        attribs = {
                'currency':'USD',
        'value-date':'2014-01-01',

        }
        element = E('value','1234',attribs)

        self.parser_201.iati_organisations__iati_organisation__recipient_org_budget__value(element)
        model = self.parser_201.get_model('RecipientOrgBudget')
        """ :type : org_models.RecipientOrgBudget """
        self.assertEqual(model.currency,self.parser_201.get_or_none(codelist_models.Currency, code=(element.attrib.get('currency'))))
        self.assertEqual(model.value,'1234')
        #assert




    '''attributes:
            'ref':'1234',

    tag:budget-line
    '''
    def test_iati_organisations__iati_organisation__recipient_org_budget__budget_line(self):
        self.test_iati_organisations__iati_organisation__recipient_org_budget()
        attribs = {
                'ref':'1234',

        }
        element = E('budget-line',attribs)

        self.parser_201.iati_organisations__iati_organisation__recipient_org_budget__budget_line(element)
        model = self.parser_201.get_model('RecipientOrgBudgetLine')
        """ :type : org_models.BudgetLine """
        self.assertEqual(model.ref,'1234')

        #assert




    '''attributes:
            'currency':'USD',
        'value-date':'2014-01-01',

    tag:value
    '''
    def test_iati_organisations__iati_organisation__recipient_org_budget__budget_line__value(self):
        self.test_iati_organisations__iati_organisation__recipient_org_budget__budget_line()
        attribs = {
                'currency':'USD',
        'value-date':'2014-01-01',

        }
        element = E('value','1234',attribs)

        self.parser_201.iati_organisations__iati_organisation__recipient_org_budget__budget_line__value(element)
        model = self.parser_201.get_model('RecipientOrgBudgetLine')
        self.assertEqual(model.currency,self.parser_201.get_or_none(codelist_models.Currency, code=(element.attrib.get('currency'))))
        self.assertEqual(model.value,'1234')

        #assert




    '''attributes:

    tag:narrative
    '''
    def test_iati_organisations__iati_organisation__recipient_org_budget__budget_line__narrative(self):
        self.test_iati_organisations__iati_organisation__recipient_org_budget__budget_line()
        attribs = {

        }
        element = E('narrative','test text',attribs)
        self.parser_201.iati_organisations__iati_organisation__recipient_org_budget__budget_line__narrative(element)
        model = self.parser_201.get_model('BudgetLineNarrative')
        self.assertEqual('test text',model.content)

        #assert




    '''attributes:

    tag:recipient-country-budget
    '''
    def test_iati_organisations__iati_organisation__recipient_country_budget(self):
        self.test_iati_organisations__iati_organisation()
        attribs = {

        }
        element = E('recipient-country-budget',attribs)
        self.parser_201.iati_organisations__iati_organisation__recipient_country_budget(element)
        model = self.parser_201.get_model('RecipientCountryBudget')
        """ :type : RecipientCountryBudget """
        #assert




    '''attributes:
            'code':'AF',

    tag:recipient-country
    '''
    def test_iati_organisations__iati_organisation__recipient_country_budget__recipient_country(self):
        self.test_iati_organisations__iati_organisation__recipient_country_budget()
        attribs = {
                'code':'AF',

        }
        element = E('recipient-country',attribs)

        self.parser_201.iati_organisations__iati_organisation__recipient_country_budget__recipient_country(element)
        model = self.parser_201.get_model('RecipientCountryBudget')
        """ :type : org_models.RecipientCountryBudget """
        self.assertEqual(model.country,self.parser_201.get_or_none(Country, code=element.attrib.get('code')))
        #assert




    '''attributes:
            'iso-date':'2014-01-01',

    tag:period-start
    '''
    def test_iati_organisations__iati_organisation__recipient_country_budget__period_start(self):
        self.test_iati_organisations__iati_organisation__recipient_country_budget()
        attribs = {
                'iso-date':'2014-01-01',

        }
        element = E('period-start',attribs)

        self.parser_201.iati_organisations__iati_organisation__recipient_country_budget__period_start(element)
        model = self.parser_201.get_model('RecipientCountryBudget')
        self.assertEqual(model.period_start,self.parser_201.validate_date('2014-01-01'))

        #assert




    '''attributes:
            'iso-date':'2014-12-31',

    tag:period-end
    '''
    def test_iati_organisations__iati_organisation__recipient_country_budget__period_end(self):
        self.test_iati_organisations__iati_organisation__recipient_country_budget()
        attribs = {
                'iso-date':'2014-12-31',

        }
        element = E('period-end',attribs)
        self.parser_201.iati_organisations__iati_organisation__recipient_country_budget__period_end(element)
        model = self.parser_201.get_model('RecipientCountryBudget')
        self.assertEqual(model.period_end,self.parser_201.validate_date('2014-12-31'))

        #assert




    '''attributes:
            'currency':'USD',
        'value-date':'2014-01-01',

    tag:value
    '''
    def test_iati_organisations__iati_organisation__recipient_country_budget__value(self):
        self.test_iati_organisations__iati_organisation__recipient_country_budget()
        attribs = {
                'currency':'USD',
        'value-date':'2014-01-01',

        }
        element = E('value','1234',attribs)
        self.parser_201.iati_organisations__iati_organisation__recipient_country_budget__value(element)
        model = self.parser_201.get_model('RecipientCountryBudget')
        self.assertEqual(model.currency,self.parser_201.get_or_none(codelist_models.Currency, code=(element.attrib.get('currency'))))
        self.assertEqual(model.value,'1234')
        #assert




    '''attributes:
            'ref':'1234',

    tag:budget-line
    '''
    def test_iati_organisations__iati_organisation__recipient_country_budget__budget_line(self):
        self.test_iati_organisations__iati_organisation__recipient_country_budget()
        attribs = {
                'ref':'1234',

        }
        element = E('budget-line',attribs)
        self.parser_201.iati_organisations__iati_organisation__recipient_country_budget__budget_line(element)
        model = self.parser_201.get_model('RecipientCountryBudgetLine')
        """ :type : org_models.BudgetLine """
        self.assertEqual(model.ref,'1234')
        #assert




    '''attributes:
            'currency':'USD',
        'value-date':'2014-01-01',

    tag:value
    '''
    def test_iati_organisations__iati_organisation__recipient_country_budget__budget_line__value(self):
        self.test_iati_organisations__iati_organisation__recipient_country_budget__budget_line()
        attribs = {
                'currency':'USD',
        'value-date':'2014-01-01',

        }
        element = E('value','1234',attribs)
        model = self.parser_201.get_model('Organisation')
        self.parser_201.iati_organisations__iati_organisation__recipient_country_budget__budget_line__value(element)
        model = self.parser_201.get_model('RecipientCountryBudgetLine')
        self.assertEqual(model.currency,self.parser_201.get_or_none(codelist_models.Currency, code=(element.attrib.get('currency'))))
        self.assertEqual(model.value,'1234')
        #assert




    '''attributes:

    tag:narrative
    '''
    def test_iati_organisations__iati_organisation__recipient_country_budget__budget_line__narrative(self):
        self.test_iati_organisations__iati_organisation__recipient_country_budget__budget_line()
        attribs = {

        }
        element = E('narrative','test text',attribs)
        self.parser_201.iati_organisations__iati_organisation__recipient_country_budget__budget_line__narrative(element)
        model = self.parser_201.get_model('BudgetLineNarrative')
        self.assertEqual('test text',model.content)
        #assert




    '''attributes:
            'format':'application/vnd.oasis.opendocument.text',
        'url':'http:www.example.org/docs/report_en.odt',

    tag:document-link
    '''
    def test_iati_organisations__iati_organisation__document_link(self):
        self.test_iati_organisations__iati_organisation()
        attribs = {
                'format':'application/vnd.oasis.opendocument.text',
        'url':'http:www.example.org/docs/report_en.odt',

        }
        element = E('document-link',attribs)
        self.parser_201.iati_organisations__iati_organisation__document_link(element)
        model = self.parser_201.get_model('DocumentLink')
        """ :type : org_models.DocumentLink """
        self.assertEqual(model.url,element.attrib.get('url'))
        self.assertEqual(model.file_format,self.parser_201.get_or_none(codelist_models.FileFormat, code=element.attrib.get('format')))

        #assert




    def test_iati_organisations__iati_organisation__document_link__title(self):
        self.test_iati_organisations__iati_organisation__document_link()
        attribs = {

        }
        element = E('title',attribs)
        self.parser_201.iati_organisations__iati_organisation__document_link__title(element)




    '''attributes:

    tag:narrative
    '''
    def test_iati_organisations__iati_organisation__document_link__title__narrative(self):
        self.test_iati_organisations__iati_organisation__document_link__title()
        attribs = {

        }
        element = E('narrative','test text',attribs)
        self.parser_201.iati_organisations__iati_organisation__document_link__title__narrative(element)
        model = self.parser_201.get_model('DocumentLinkTitleNarrative')
        self.assertEqual('test text',model.content)




    '''attributes:
            'code':'B01',

    tag:category
    '''
    def test_iati_organisations__iati_organisation__document_link__category(self):
        self.test_iati_organisations__iati_organisation__document_link()
        attribs = {
                'code':'B01',

        }
        element = E('category',attribs)

        self.parser_201.iati_organisations__iati_organisation__document_link__category(element)
        model = self.parser_201.get_model('DocumentLink')
        #assert




    '''attributes:
            'code':'en',

    tag:language
    '''
    def test_iati_organisations__iati_organisation__document_link__language(self):
        self.test_iati_organisations__iati_organisation__document_link()
        attribs = {
                'code':'en',

        }
        element = E('language',attribs)

        self.parser_201.iati_organisations__iati_organisation__document_link__language(element)
        model = self.parser_201.get_model('DocumentLink')
        """ :type : org_models.DocumentLink """
        self.assertEqual(model.language,self.parser_201.get_or_none(codelist_models.Language, code=element.attrib.get('code')))

        #assert




    '''attributes:
            'code':'AF',

    tag:recipient-country
    '''
    def test_iati_organisations__iati_organisation__document_link__recipient_country(self):
        self.test_iati_organisations__iati_organisation__document_link()
        model = self.parser_201.get_model('DocumentLink')
        model.save()
        attribs = {
                'code':'AF',

        }
        element = E('recipient-country',attribs)

        self.parser_201.iati_organisations__iati_organisation__document_link__recipient_country(element)

        #assert


