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

from iati.parser.IATI_1_03 import Parse as Parser_103
from iati.parser.IATI_1_05 import Parse as Parser_105
from iati.parser.IATI_2_01 import Parse as Parser_201
from iati_organisation.organisation_2_01 import Parse as OrgParse_201
from iati_organisation.organisation_1_05 import Parse as OrgPArse_105


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


def setUpModule():
    fixtures = ['test_publisher.json', 'test_codelists.json', 'test_vocabulary', 'test_geodata.json']

    for fixture in fixtures:
        management.call_command("loaddata", fixture)

def tearDownModule():
    management.call_command('flush', interactive=False, verbosity=0)

class ParserSetupTestCase(DjangoTestCase):

    # fixtures = ['test_publisher.json', 'test_codelists.json', 'test_vocabulary', 'test_geodata.json']

    def _get_organisation(self, iati_identifier):
        return org_models.Organisation.objects.get(id=iati_identifier)

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


        dummy_source = IatiXmlSource.objects.get(id=2)

        self.parser_103 = ParseIATI(dummy_source, self.iati_103).get_parser()
        self.parser_104 = ParseIATI(dummy_source, self.iati_104).get_parser()
        self.parser_105 = ParseIATI(dummy_source, self.iati_105).get_parser()
        self.parser_201 = ParseIATI(dummy_source, self.iati_201).get_parser()

        assert(isinstance(self.parser_103, OrgPArse_105))
        assert(isinstance(self.parser_104, OrgPArse_105))
        assert(isinstance(self.parser_105, OrgPArse_105))
        assert(isinstance(self.parser_201, OrgParse_201))

        # todo: self.assertTrue source was handled appropriately
        # self.self.assertTrueEqual(self.parser_103.iati_source, self.parser_104.iati_source, self.parser_105.iati_source, self.parser_201.iati_source)

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

        # sample attributes on iati-activity xml
        self.attrs = {
            # "xml:lang": "en",
            "default-currency": "USD",
            "last-updated-datetime": datetime.datetime.now().isoformat(' '),
        }

        # default activity model fields
        self.defaults = {
            "hierarchy": 1,
            "default_lang": "en",
        }

        self.test_parser = self.parser_201
        iati_organisation = E("iati-organisation", **self.attrs)
        iati_organisation.append(E("organisation-identifier", self.iati_identifier))
        self.iati_201.append(iati_organisation)
        self.iati_201.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en" # ISO 639-1:2002
        # print(etree.tostring(self.iati_201, pretty_print=True))

        organisation = org_models.Organisation(iati_version_id="2.01")
        self.parser_201.register_model('Organisation', organisation)



    '''attributes:
            'default-currency':'EUR',
        'last-updated-datetime':'2014-09-10T07:15:37Z',
        '{http://www.w3.org/XML/1998/namespace}lang':'en',

    tag:iati-organisation
    '''
    def test_iati_organisations__iati_organisation(self):
        attribs = {
                'default-currency':'EUR',
        'last-updated-datetime':'2014-09-10T07:15:37Z',
        '{http://www.w3.org/XML/1998/namespace}lang':'en',

        }
        element = E('iati-organisation',E('organisation-identifier','AA-AAA-123456789',{}),attribs)

        self.test_parser.iati_organisations__iati_organisation(element)
        org = self.test_parser.get_model('Organisation')
        """:type : org_models.Organisation """
        self.assertEqual(org.code,'AA-AAA-123456789')
        currency = self.test_parser.get_or_none(codelist_models.Currency, code=element.attrib.get('default-currency'))
        language = self.test_parser.get_or_none(codelist_models.Language, code='en')
        self.assertEqual(org.default_currency , currency)
        self.assertEqual(org.default_lang,language)
        self.assertEqual(org.last_updated_datetime,self.test_parser.validate_date(element.attrib.get('last-updated-datetime')))
        self.assertEqual(org.code,"AA-AAA-123456789")


        #assert








    '''attributes:

    tag:name
    '''
    def test_iati_organisations__iati_organisation__name(self):
        attribs = {

        }
        element = E('name',attribs)
        self.test_parser.iati_organisations__iati_organisation__name(element)
        org = self.test_parser.get_model('Organisation')
        """:type : org_models.Organisation """
        attribs = {

        }
        element = E('narrative','test narrative name',attribs)

        self.test_parser.iati_organisations__iati_organisation__name__narrative(element)
        model = self.test_parser.get_model('NameNarrative')
        """ :type : org_models.Narrative """
        self.assertEqual('test narrative name',model.content)
        #assert



        #assert







    '''attributes:
            'ref':'AA-AAA-123456789',
        'type':'40',
        'secondary-reporter':'0',

    tag:reporting-org
    '''
    def test_iati_organisations__iati_organisation__reporting_org(self):
        self.test_iati_organisations__iati_organisation()
        attribs = {
                'ref':'AA-AAA-123456789',
        'type':'40',
        'secondary-reporter':'0',

        }
        element = E('reporting-org',attribs)

        self.test_parser.iati_organisations__iati_organisation__reporting_org(element)
        model = self.test_parser.get_model('ReportingOrg')
        """ :type : org_models.ReportingOrg """
        self.assertEqual(model.reporting_org_identifier,'AA-AAA-123456789')
        self.assertEqual(model.org_type_id,'40')
        self.assertEqual(model.secondary_reporter,False)





    '''attributes:

    tag:narrative
    '''
    def test_iati_organisations__iati_organisation__reporting_org__narrative(self):
        self.test_iati_organisations__iati_organisation__reporting_org()

        attribs = {

        }
        element = E('narrative','test narrative text',attribs)

        self.test_parser.iati_organisations__iati_organisation__reporting_org__narrative(element)
        model = self.test_parser.get_model('ReportingOrgNarrative')
        self.assertEqual('test narrative text',model.content)
        #assert




    '''attributes:

    tag:total-budget
    '''
    def test_iati_organisations__iati_organisation__total_budget(self):
        self.test_iati_organisations__iati_organisation()
        attribs = {

        }
        element = E('total-budget',attribs)

        self.test_parser.iati_organisations__iati_organisation__total_budget(element)
        model = self.test_parser.get_model('TotalBudget')
        #assert




    '''attributes:
            'iso-date':'2014-01-01',

    tag:period-start
    '''
    def test_iati_organisations__iati_organisation__total_budget__period_start(self):
        self.test_iati_organisations__iati_organisation__total_budget()
        attribs = {
                'iso-date':'2014-01-01',

        }
        element = E('period-start',attribs)
        self.test_parser.iati_organisations__iati_organisation__total_budget__period_start(element)
        model = self.test_parser.get_model('TotalBudget')
        """:type : org_models.TotalBudget """
        self.assertEqual(model.period_start,self.test_parser.validate_date('2014-01-01'))
        #assert




    '''attributes:
            'iso-date':'2014-12-31',

    tag:period-end
    '''
    def test_iati_organisations__iati_organisation__total_budget__period_end(self):
        self.test_iati_organisations__iati_organisation__total_budget()
        attribs = {
                'iso-date':'2014-12-31',

        }
        element = E('period-end',attribs)
        self.test_parser.iati_organisations__iati_organisation__total_budget__period_end(element)
        model = self.test_parser.get_model('TotalBudget')
        """:type : org_models.TotalBudget """
        self.assertEqual(model.period_end,self.test_parser.validate_date('2014-12-31'))
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
        self.test_parser.iati_organisations__iati_organisation__total_budget__value(element)
        model = self.test_parser.get_model('TotalBudget')
        """:type : org_models.TotalBudget """
        self.assertEqual(model.currency,self.test_parser.get_or_none(codelist_models.Currency, code=(element.attrib.get('currency'))))
        self.assertEqual(model.value,'123')
        self.assertEqual(model.value_date,self.test_parser.validate_date('2014-01-01'))

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

        self.test_parser.iati_organisations__iati_organisation__total_budget__budget_line(element)
        model = self.test_parser.get_model('TotalBudgetLine')
        """ :type : org_models.BudgetLine """
        self.assertEqual(model.ref,'1234')
        attribs = {

        }
        element = E('narrative','test narrative text',attribs)
        self.test_parser.iati_organisations__iati_organisation__total_budget__budget_line__narrative(element)
        model = self.test_parser.get_model('BudgetLineNarrative')
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
        self.test_parser.iati_organisations__iati_organisation__total_budget__budget_line__value(element)
        model = self.test_parser.get_model('TotalBudgetLine')
        """ :type : org_models.BudgetLine """
        self.assertEqual(model.currency,self.test_parser.get_or_none(codelist_models.Currency, code=(element.attrib.get('currency'))))
        self.assertEqual(model.value_date,self.test_parser.validate_date(element.attrib.get('value-date')))
        #assert





    '''attributes:

    tag:recipient-org-budget
    '''
    def test_iati_organisations__iati_organisation__recipient_org_budget(self):
        self.test_iati_organisations__iati_organisation()
        attribs = {

        }
        element = E('recipient-org-budget',attribs)
        self.test_parser.iati_organisations__iati_organisation__recipient_org_budget(element)
        model = self.test_parser.get_model('RecipientOrgBudget')

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

        self.test_parser.iati_organisations__iati_organisation__recipient_org_budget__recipient_org(element)
        model = self.test_parser.get_model('RecipientOrgBudget')
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

        self.test_parser.iati_organisations__iati_organisation__recipient_org_budget__recipient_org__narrative(element)
        model = self.test_parser.get_model('RecipientOrgBudgetNarrative')
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
        self.test_parser.iati_organisations__iati_organisation__recipient_org_budget__period_start(element)
        model = self.test_parser.get_model('RecipientOrgBudget')
        """ :type : org_models.RecipientOrgBudget """
        self.assertEqual(model.period_start,self.test_parser.validate_date('2014-01-01'))

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
        self.test_parser.iati_organisations__iati_organisation__recipient_org_budget__period_end(element)
        model = self.test_parser.get_model('RecipientOrgBudget')
        """ :type : org_models.RecipientOrgBudget """
        self.assertEqual(model.period_end,self.test_parser.validate_date('2014-12-31'))





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

        self.test_parser.iati_organisations__iati_organisation__recipient_org_budget__value(element)
        model = self.test_parser.get_model('RecipientOrgBudget')
        """ :type : org_models.RecipientOrgBudget """
        self.assertEqual(model.currency,self.test_parser.get_or_none(codelist_models.Currency, code=(element.attrib.get('currency'))))
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

        self.test_parser.iati_organisations__iati_organisation__recipient_org_budget__budget_line(element)
        model = self.test_parser.get_model('RecipientOrgBudgetLine')
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

        self.test_parser.iati_organisations__iati_organisation__recipient_org_budget__budget_line__value(element)
        model = self.test_parser.get_model('RecipientOrgBudgetLine')
        self.assertEqual(model.currency,self.test_parser.get_or_none(codelist_models.Currency, code=(element.attrib.get('currency'))))
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
        self.test_parser.iati_organisations__iati_organisation__recipient_org_budget__budget_line__narrative(element)
        model = self.test_parser.get_model('BudgetLineNarrative')
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
        self.test_parser.iati_organisations__iati_organisation__recipient_country_budget(element)
        model = self.test_parser.get_model('RecipientCountryBudget')
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

        self.test_parser.iati_organisations__iati_organisation__recipient_country_budget__recipient_country(element)
        model = self.test_parser.get_model('RecipientCountryBudget')
        """ :type : org_models.RecipientCountryBudget """
        self.assertEqual(model.country,self.test_parser.get_or_none(Country, code=element.attrib.get('code')))
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

        self.test_parser.iati_organisations__iati_organisation__recipient_country_budget__period_start(element)
        model = self.test_parser.get_model('RecipientCountryBudget')
        self.assertEqual(model.period_start,self.test_parser.validate_date('2014-01-01'))

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
        self.test_parser.iati_organisations__iati_organisation__recipient_country_budget__period_end(element)
        model = self.test_parser.get_model('RecipientCountryBudget')
        self.assertEqual(model.period_end,self.test_parser.validate_date('2014-12-31'))

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
        self.test_parser.iati_organisations__iati_organisation__recipient_country_budget__value(element)
        model = self.test_parser.get_model('RecipientCountryBudget')
        self.assertEqual(model.currency,self.test_parser.get_or_none(codelist_models.Currency, code=(element.attrib.get('currency'))))
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
        self.test_parser.iati_organisations__iati_organisation__recipient_country_budget__budget_line(element)
        model = self.test_parser.get_model('RecipientCountryBudgetLine')
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
        model = self.test_parser.get_model('Organisation')
        self.test_parser.iati_organisations__iati_organisation__recipient_country_budget__budget_line__value(element)
        model = self.test_parser.get_model('RecipientCountryBudgetLine')
        self.assertEqual(model.currency,self.test_parser.get_or_none(codelist_models.Currency, code=(element.attrib.get('currency'))))
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
        self.test_parser.iati_organisations__iati_organisation__recipient_country_budget__budget_line__narrative(element)
        model = self.test_parser.get_model('BudgetLineNarrative')
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
        self.test_parser.iati_organisations__iati_organisation__document_link(element)
        model = self.test_parser.get_model('DocumentLink')
        """ :type : org_models.DocumentLink """
        self.assertEqual(model.url,element.attrib.get('url'))
        self.assertEqual(model.file_format,self.test_parser.get_or_none(codelist_models.FileFormat, code=element.attrib.get('format')))

        #assert




    def test_iati_organisations__iati_organisation__document_link__title(self):
        self.test_iati_organisations__iati_organisation__document_link()
        attribs = {

        }
        element = E('title',attribs)
        self.test_parser.iati_organisations__iati_organisation__document_link__title(element)




    '''attributes:

    tag:narrative
    '''
    def test_iati_organisations__iati_organisation__document_link__title__narrative(self):
        self.test_iati_organisations__iati_organisation__document_link__title()
        attribs = {

        }
        element = E('narrative','test text',attribs)
        self.test_parser.iati_organisations__iati_organisation__document_link__title__narrative(element)
        model = self.test_parser.get_model('DocumentLinkTitleNarrative')
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

        self.test_parser.iati_organisations__iati_organisation__document_link__category(element)
        model = self.test_parser.get_model('DocumentLink')
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

        self.test_parser.iati_organisations__iati_organisation__document_link__language(element)
        model = self.test_parser.get_model('DocumentLink')
        """ :type : org_models.DocumentLink """
        self.assertEqual(model.language,self.test_parser.get_or_none(codelist_models.Language, code=element.attrib.get('code')))

        #assert




    '''attributes:
            'code':'AF',

    tag:recipient-country
    '''
    def test_iati_organisations__iati_organisation__document_link__recipient_country(self):
        self.test_iati_organisations__iati_organisation__document_link()
        model = self.test_parser.get_model('DocumentLink')
        model.save()
        attribs = {
                'code':'AF',

        }
        element = E('recipient-country',attribs)

        self.test_parser.iati_organisations__iati_organisation__document_link__recipient_country(element)

        #assert


