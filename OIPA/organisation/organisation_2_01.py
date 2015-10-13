
import re

from iati.genericXmlParser import XMLParser
from iati import models
from models import (
    Organisation,
    Name,
    ReportingOrg,
    TotalBudget,
    Narrative,
    BudgetLine,
    RecipientOrgBudget,
    RecipientCountryBudget,
    DocumentLink,
    DocumentLinkTitle)
from geodata.models import Country

from django.conf import settings

_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[-\s]+')


class Parse(XMLParser):

    VERSION = '2.01'
    default_lang = 'en'
    organisation_identifier = ''

    def __init__(self):
        super(XMLParser, self).__init__()

    def add_narrative(self, element, parent):
        narrative = Narrative()
        lang = self.default_lang
        if '{http://www.w3.org/XML/1998/namespace}lang' in element.attrib:
            lang = element.attrib['{http://www.w3.org/XML/1998/namespace}lang']

        if element.text is None or element.text == '':
            return
        narrative.language = self.cached_db_call(models.Language, lang)
        narrative.content = element.text
        narrative.organisation_identifier = self.organisation_identifier
        narrative.parent_object = parent
        narrative.save()

    def __init__(self):
        pass

    '''atributes:
        default-currency:EUR
        last-updated-datetime:2014-09-10T07:15:37Z
        {http://www.w3.org/XML/1998/namespace}lang:en

    tag:iati-organisation
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 6 iati_version =2.01'''

    def iati_organisations__iati_organisation(self, element):
        organisation = Organisation()
        organisation.organisation_identifier = element.xpath('organisation-identifier/text()')[0]
        self.organisation_identifier = organisation.organisation_identifier
        organisation.code = self.organisation_identifier
        organisation.last_updated_datetime = self.validate_date(element.attrib.get('last_updated_datetime'))
        if '{http://www.w3.org/XML/1998/namespace}lang' in element.attrib:
            organisation.default_lang = element.attrib['{http://www.w3.org/XML/1998/namespace}lang']
        organisation.iati_version_id = self.cached_db_call_no_version(models.Versionself.VERSION, createNew=True)

        organisation.save()
        # add to reporting organisation and recipient_organisation
        RecipientOrgBudget.objects.filter(recipient_org_identifier=self.organisation_identifier).update(recipient_org=organisation)
        ReportingOrg.objects.filter(reporting_org_identifier=self.organisation_identifier).update(reporting_org=organisation)
        self.set_func_model(organisation)
        # store element
        return element

    '''atributes:

    tag:organisation-identifier
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 8 iati_version =2.01'''

    def iati_organisations__iati_organisation__organisation_identifier(self, element):
        # already set in iati_organisation
        return element

    '''atributes:

    tag:name
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 11 iati_version =2.01'''

    def iati_organisations__iati_organisation__name(self, element):
        model = self.get_func_parent_model()
        name = Name()
        name.organisation = model
        name.save()

        return element

    '''atributes:

    tag:narrative
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 12 iati_version =2.01'''

    def iati_organisations__iati_organisation__name__narrative(self, element):
        model = self.get_func_parent_model()
        self.add_narrative(element, model)
        # store element
        return element

    '''atributes:
        ref:AA-AAA-123456789
        type:40
        secondary-reporter:0

    tag:reporting-org
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 17 iati_version =2.01'''

    def iati_organisations__iati_organisation__reporting_org(self, element):
        model = self.get_func_parent_model()
        reporting_org = ReportingOrg()
        reporting_org.organisation = model
        reporting_org.reporting_org_id = element.attrib.get('ref')
        type_ref = element.attrib.get('type')
        if self.isInt(type_ref) and self.cached_db_call(models.OrganisationType, type_ref) != None:
            org_type = self.cached_db_call(models.OrganisationType, type_ref)
            reporting_org.org_type = org_type
        reporting_org.save()
        self.set_func_model(reporting_org)

        return element

    '''atributes:

    tag:narrative
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 18 iati_version =2.01'''

    def iati_organisations__iati_organisation__reporting_org__narrative(self, element):
        model = self.get_func_parent_model()
        self.add_narrative(element, model)
        # store element
        return element

    '''atributes:

    tag:total-budget
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 23 iati_version =2.01'''

    def iati_organisations__iati_organisation__total_budget(self, element):
        model = self.get_func_parent_model()
        total_budget = TotalBudget()
        total_budget.organisation = model

        # store element
        return element

    '''atributes:
        iso-date:2014-01-01

    tag:period-start
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 24 iati_version =2.01'''

    def iati_organisations__iati_organisation__total_budget__period_start(self, element):
        model = self.get_func_parent_model()
        model.period_start = self.validate_date(element.attrib.get('iso-date'))

        # store element
        return element

    '''atributes:
        iso-date:2014-12-31

    tag:period-end
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 25 iati_version =2.01'''

    def iati_organisations__iati_organisation__total_budget__period_end(self, element):
        model = self.get_func_parent_model()
        model.period_end = self.validate_date(element.attrib.get('iso-date'))
        # store element
        return element

    '''atributes:
        currency:USD
        value-date:2014-01-01

    tag:value
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 26 iati_version =2.01'''

    def iati_organisations__iati_organisation__total_budget__value(self, element):
        model = self.get_func_parent_model()
        model.currency = self.cached_db_call_no_version(models.Currency, element.attrib.get('currency'))
        model.value = element.attrib.get('value')
        # store element
        return element

    '''atributes:
        ref:1234

    tag:budget-line
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 27 iati_version =2.01'''

    def iati_organisations__iati_organisation__total_budget__budget_line(self, element):
        model = self.get_func_parent_model()
        budget_line = BudgetLine()
        budget_line.ref = element.attrib.get('ref')
        budget_line.parent = model
        self.set_func_model(budget_line)
        # store element
        return element

    '''atributes:
        currency:USD
        value-date:2014-01-01

    tag:value
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 28 iati_version =2.01'''

    def iati_organisations__iati_organisation__total_budget__budget_line__value(self, element):
        model = self.get_func_parent_model()
        model.currency = self.cached_db_call_no_version(models.Currency, element.attrib.get('currency'))
        model.value = element.attrib.get('value')
        # store element
        return element

    '''atributes:

    tag:narrative
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 29 iati_version =2.01'''

    def iati_organisations__iati_organisation__total_budget__budget_line__narrative(self, element):
        model = self.get_func_parent_model()
        self.add_narrative(element, model)
        # store element
        return element

    '''atributes:

    tag:recipient-org-budget
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 34 iati_version =2.01'''

    def iati_organisations__iati_organisation__recipient_org_budget(self, element):
        model = self.get_func_parent_model()
        recipient_org_budget = RecipientOrgBudget()
        recipient_org_budget.organisation = model
        self.set_func_model(recipient_org_budget)
        # store element
        return element

    '''atributes:
        ref:AA-ABC-1234567

    tag:recipient-org
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 35 iati_version =2.01'''

    def iati_organisations__iati_organisation__recipient_org_budget__recipient_org(self, element):
        model = self.get_func_parent_model()
        model.recipient_org_identifier = element.attrib.get('ref')
        if Organisation.objects.filter(code=element.attrib.get('ref')).exists():
            model.recipient_org = Organisation.objects.get(pk=element.attrib.get('ref'))

        # store element
        return element

    '''atributes:

    tag:narrative
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 36 iati_version =2.01'''

    def iati_organisations__iati_organisation__recipient_org_budget__recipient_org__narrative(self, element):
        model = self.get_func_parent_model()
        self.add_narrative(element, model)
        # store element
        return element

    '''atributes:
        iso-date:2014-01-01

    tag:period-start
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 38 iati_version =2.01'''

    def iati_organisations__iati_organisation__recipient_org_budget__period_start(self, element):
        model = self.get_func_parent_model()
        model.period_start = self.validate_date(element.attrib.get('iso-date'))

        # store element
        return element

    '''atributes:
        iso-date:2014-12-31

    tag:period-end
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 39 iati_version =2.01'''

    def iati_organisations__iati_organisation__recipient_org_budget__period_end(self, element):
        model = self.get_func_parent_model()
        model.period_end = self.validate_date(element.attrib.get('iso-date'))
        # store element
        return element

    '''atributes:
        currency:USD
        value-date:2014-01-01

    tag:value
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 40 iati_version =2.01'''

    def iati_organisations__iati_organisation__recipient_org_budget__value(self, element):
        model = self.get_func_parent_model()
        model.currency = self.cached_db_call_no_version(models.Currency, element.attrib.get('currency'))
        model.value = element.attrib.get('value')
        # store element
        return element

    '''atributes:
        ref:1234

    tag:budget-line
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 41 iati_version =2.01'''

    def iati_organisations__iati_organisation__recipient_org_budget__budget_line(self, element):
        model = self.get_func_parent_model()
        budget_line = BudgetLine()
        budget_line.ref = element.attrib.get('ref')
        budget_line.parent = model
        self.set_func_model(budget_line)
        # store element
        return element

    '''atributes:
        currency:USD
        value-date:2014-01-01

    tag:value
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 42 iati_version =2.01'''

    def iati_organisations__iati_organisation__recipient_org_budget__budget_line__value(self, element):
        model = self.get_func_parent_model()
        model.currency = self.cached_db_call_no_version(models.Currency, element.attrib.get('currency'))
        model.value = element.attrib.get('value')
        # store element
        return element

    '''atributes:

    tag:narrative
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 43 iati_version =2.01'''

    def iati_organisations__iati_organisation__recipient_org_budget__budget_line__narrative(self, element):
        model = self.get_func_parent_model()
        self.add_narrative(element, model)
        # store element
        return element

    '''atributes:

    tag:recipient-country-budget
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 48 iati_version =2.01'''

    def iati_organisations__iati_organisation__recipient_country_budget(self, element):
        model = self.get_func_parent_model()
        recipient_country_budget = RecipientCountryBudget()
        recipient_country_budget.organisation = model
        self.set_func_model(recipient_country_budget)
        # store element
        return element

    '''atributes:
        code:AF

    tag:recipient-country
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 49 iati_version =2.01'''

    def iati_organisations__iati_organisation__recipient_country_budget__recipient_country(self, element):
        model = self.get_func_parent_model()
        model.country = self.cached_db_call_no_version(Country, element.attrib.get('code'))

        # store element
        return element

    '''atributes:
        iso-date:2014-01-01

    tag:period-start
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 50 iati_version =2.01'''

    def iati_organisations__iati_organisation__recipient_country_budget__period_start(self, element):
        model = self.get_func_parent_model()
        model.period_start = self.validate_date(element.attrib.get('iso-date'))
        # store element
        return element

    '''atributes:
        iso-date:2014-12-31

    tag:period-end
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 51 iati_version =2.01'''

    def iati_organisations__iati_organisation__recipient_country_budget__period_end(self, element):
        model = self.get_func_parent_model()
        model.period_end = self.validate_date(element.attrib.get('iso-date'))
        # store element
        return element

    '''atributes:
        currency:USD
        value-date:2014-01-01

    tag:value
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 52 iati_version =2.01'''

    def iati_organisations__iati_organisation__recipient_country_budget__value(self, element):
        model = self.get_func_parent_model()
        model.currency = self.cached_db_call_no_version(models.Currency, element.attrib.get('currency'))
        model.value = element.attrib.get('value')
        # store element
        return element

    '''atributes:
        ref:1234

    tag:budget-line
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 53 iati_version =2.01'''

    def iati_organisations__iati_organisation__recipient_country_budget__budget_line(self, element):
        model = self.get_func_parent_model()
        budget_line = BudgetLine()
        budget_line.ref = element.attrib.get('ref')
        budget_line.parent = model
        self.set_func_model(budget_line)
        # store element
        return element

    '''atributes:
        currency:USD
        value-date:2014-01-01

    tag:value
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 54 iati_version =2.01'''

    def iati_organisations__iati_organisation__recipient_country_budget__budget_line__value(self, element):
        model = self.get_func_parent_model()
        model.currency = self.cached_db_call_no_version(models.Currency, element.attrib.get('currency'))
        model.value = element.attrib.get('value')
        # store element
        return element

    '''atributes:

    tag:narrative
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 55 iati_version =2.01'''

    def iati_organisations__iati_organisation__recipient_country_budget__budget_line__narrative(self, element):
        model = self.get_func_parent_model()
        self.add_narrative(element, model)
        # store element
        return element

    '''atributes:
        format:application/vnd.oasis.opendocument.text
        url:http:www.example.org/docs/report_en.odt

    tag:document-link
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 60 iati_version =2.01'''

    def iati_organisations__iati_organisation__document_link(self, element):
        model = self.get_func_parent_model()
        document_link = DocumentLink()
        document_link.organisation = model
        document_link.url = element.attrib.get('url')
        document_link.file_format = self.cached_db_call(models.FileFormat, element.attrib.get('format'), createNew=True)
        self.set_func_model(document_link)

        # store element
        return element

    '''atributes:

    tag:title
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 61 iati_version =2.01'''

    def iati_organisations__iati_organisation__document_link__title(self, element):
        model = self.get_func_parent_model()
        document_link_title = DocumentLinkTitle()
        document_link_title.document_link = model
        self.set_func_model(document_link_title)

        # store element
        return element

    '''atributes:

    tag:narrative
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 62 iati_version =2.01'''

    def iati_organisations__iati_organisation__document_link__title__narrative(self, element):
        model = self.get_func_parent_model()
        self.add_narrative(element, model)
        # store element
        return element

    '''atributes:
        code:B01

    tag:category
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 64 iati_version =2.01'''

    def iati_organisations__iati_organisation__document_link__category(self, element):
        model = self.get_func_parent_model()
        document_category = self.cached_db_call(models.DocumentCategory, element.attrib.get('code'))
        model.categories.add(document_category)
        # store element
        return element

    '''atributes:
        code:en

    tag:language
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 65 iati_version =2.01'''

    def iati_organisations__iati_organisation__document_link__language(self, element):
        model = self.get_func_parent_model()
        model.language = self.cached_db_call(models.Language, element.attrib.get('code'))
        # store element
        return element

    '''atributes:
        code:AF

    tag:recipient-country
    found in
    https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml
    at line 66 iati_version =2.01'''

    def iati_organisations__iati_organisation__document_link__recipient_country(self, element):
        model = self.get_func_parent_model()
        country = self.cached_db_call(Country, element.attrib.get('code'))
        model.recipient_countries.add(country)

        # store element
        return element
