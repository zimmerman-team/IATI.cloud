import re

from iati.parser.IATI_2_01 import Parse as IATI_201_Parser
from iati_codelists import models as codelist_models

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

_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[-\s]+')


class Parse(IATI_201_Parser):
    VERSION = '2.01'
    default_lang = 'en'
    organisation_identifier = ''

    # TODO: remove this inheritance - 2015-12-10
    def __init__(self, *args, **kwargs):
        super(IATI_201_Parser, self).__init__(*args, **kwargs)

    def add_narrative(self, element, parent):
        default_lang = self.default_lang  # set on activity (if set)
        lang = element.attrib.get('{http://www.w3.org/XML/1998/namespace}lang', default_lang)
        text = element.text

        language = self.get_or_none(codelist_models.Language, code=lang)

        if not language: raise self.RequiredFieldError(
            "narrative: must specify default_lang on activities or language on the element itself")
        if not text: raise self.RequiredFieldError("narrative: must contain text")
        if not parent: raise self.RequiredFieldError("parent", "Narrative: parent object must be passed")
        narrative = Narrative()
        lang = self.default_lang
        if '{http://www.w3.org/XML/1998/namespace}lang' in element.attrib:
            lang = element.attrib['{http://www.w3.org/XML/1998/namespace}lang']

        if element.text is None or element.text == '':
            return
        narrative.language = language
        narrative.content = element.text
        narrative.organisation_identifier = self.organisation_identifier
        narrative.parent_object = parent
        # TODO: handle this differently (also: breaks tests)
        register_name = parent.__class__.__name__ + "Narrative"
        self.register_model(register_name, narrative)

    def _get_currency_or_raise(self, currency):
        """
        get default currency if not available for currency-related fields
        """
        if not currency:
            currency = getattr(self.get_model('Organisation'), 'default_currency')
            if not currency: raise self.RequiredFieldError("currency", "currency: currency is not set and default-currency is not set on activity as well")

        return currency

    '''atributes:
        default-currency:EUR
        last-updated-datetime:2014-09-10T07:15:37Z
        {http://www.w3.org/XML/1998/namespace}lang:en

    tag:iati-organisation'''

    def iati_organisations__iati_organisation(self, element):
        organisation = Organisation()
        organisation.organisation_identifier = element.xpath('organisation-identifier/text()')[0]

        self.organisation_identifier = organisation.organisation_identifier
        organisation.code = self.organisation_identifier
        organisation.original_ref = self.organisation_identifier
        organisation.last_updated_datetime = self.validate_date(element.attrib.get('last-updated-datetime'))
        if '{http://www.w3.org/XML/1998/namespace}lang' in element.attrib:
            organisation.default_lang = self.get_or_none(codelist_models.Language, code=element.attrib.get('{http://www.w3.org/XML/1998/namespace}lang'))
        organisation.iati_version_id = self.VERSION
        self.default_currency = self.get_or_none(codelist_models.Currency, code=element.attrib.get('default-currency'))
        organisation.default_currency = self.get_or_none(codelist_models.Currency, code=element.attrib.get('default-currency'))
        organisation.save()
        # add to reporting organisation and recipient_organisation
        RecipientOrgBudget.objects.filter(recipient_org_identifier=self.organisation_identifier).update(
            recipient_org=organisation)
        ReportingOrg.objects.filter(reporting_org_identifier=self.organisation_identifier).update(
            reporting_org=organisation)
        self.register_model('Organisation', organisation)
        # store element
        return element

    '''atributes:

    tag:organisation-identifier'''

    def iati_organisations__iati_organisation__organisation_identifier(self, element):
        # already set in iati_organisation
        return element

    '''atributes:

    tag:name'''

    def iati_organisations__iati_organisation__name(self, element):
        model = self.get_model('Organisation')
        name = Name()
        name.organisation = model
        self.register_model('Name', name)

        return element

    '''atributes:

    tag:narrative'''

    def iati_organisations__iati_organisation__name__narrative(self, element):
        model = self.get_model('Name')
        self.add_narrative(element, model)
        # store element
        return element

    '''atributes:
        ref:AA-AAA-123456789
        type:40
        secondary-reporter:0

    tag:reporting-org'''

    def iati_organisations__iati_organisation__reporting_org(self, element):
        model = self.get_model('Organisation')
        reporting_org = ReportingOrg()
        reporting_org.organisation = model
        reporting_org.reporting_org_identifier = element.attrib.get('ref')
        type_ref = element.attrib.get('type')
        if self.isInt(type_ref) and self.get_or_none(codelist_models.OrganisationType, code=type_ref) != None:
            org_type = self.get_or_none(codelist_models.OrganisationType, code=type_ref)
            reporting_org.org_type = org_type
        self.register_model('ReportingOrg', reporting_org)

        return element

    '''atributes:

    tag:narrative'''

    def iati_organisations__iati_organisation__reporting_org__narrative(self, element):
        model = self.get_model('ReportingOrg')
        self.add_narrative(element, model)
        # store element
        return element

    '''atributes:

    tag:total-budget'''

    def iati_organisations__iati_organisation__total_budget(self, element):
        model = self.get_model('Organisation')
        total_budget = TotalBudget()
        total_budget.organisation = model
        self.register_model('TotalBudget', total_budget)
        # store element
        return element

    '''atributes:
        iso-date:2014-01-01

    tag:period-start'''

    def iati_organisations__iati_organisation__total_budget__period_start(self, element):
        model = self.get_model('TotalBudget')
        model.period_start = self.validate_date(element.attrib.get('iso-date'))

        # store element
        return element

    '''atributes:
        iso-date:2014-12-31

    tag:period-end'''

    def iati_organisations__iati_organisation__total_budget__period_end(self, element):
        model = self.get_model('TotalBudget')
        model.period_end = self.validate_date(element.attrib.get('iso-date'))
        # store element
        return element

    '''atributes:
        currency:USD
        value-date:2014-01-0

    tag:value'''

    def iati_organisations__iati_organisation__total_budget__value(self, element):
        model = self.get_model('TotalBudget')
        model.currency = self.get_or_none(codelist_models.Currency, code=self._get_currency_or_raise(element.attrib.get('currency')))
        model.value_date = self.validate_date(element.attrib.get('value-date'))
        model.value = element.text
        # store element
        return element

    '''atributes:
        ref:1234

    tag:budget-line'''

    def iati_organisations__iati_organisation__total_budget__budget_line(self, element):
        model = self.get_model('TotalBudget')
        budget_line = BudgetLine()
        budget_line.ref = element.attrib.get('ref')
        budget_line.parent = model
        self.register_model('TotalBudgetLine', budget_line)
        # store element
        return element

    '''atributes:
        currency:USD
        value-date:2014-01-01

    tag:value'''

    def iati_organisations__iati_organisation__total_budget__budget_line__value(self, element):
        model = self.get_model('TotalBudgetLine')
        model.currency = self.get_or_none(codelist_models.Currency, code=self._get_currency_or_raise(element.attrib.get('currency')))
        model.value = element.text
        model.value_date = self.validate_date(element.attrib.get('value-date'))
        # store element
        return element

    '''atributes:

    tag:narrative'''

    def iati_organisations__iati_organisation__total_budget__budget_line__narrative(self, element):
        model = self.get_model('TotalBudgetLine')

        self.add_narrative(element, model)
        # store element
        return element

    '''atributes:

    tag:recipient-org-budget'''

    def iati_organisations__iati_organisation__recipient_org_budget(self, element):
        model = self.get_model('Organisation')
        recipient_org_budget = RecipientOrgBudget()
        recipient_org_budget.organisation = model
        self.register_model('RecipientOrgBudget', recipient_org_budget)
        # store element
        return element

    '''atributes:
        ref:AA-ABC-1234567

    tag:recipient-org'''

    def iati_organisations__iati_organisation__recipient_org_budget__recipient_org(self, element):
        model = self.get_model('RecipientOrgBudget')
        model.recipient_org_identifier = element.attrib.get('ref')
        if Organisation.objects.filter(code=element.attrib.get('ref')).exists():
            model.recipient_org = Organisation.objects.get(pk=element.attrib.get('ref'))

        # store element
        return element

    '''atributes:

    tag:narrative'''

    def iati_organisations__iati_organisation__recipient_org_budget__recipient_org__narrative(self, element):
        model = self.get_model('RecipientOrgBudget')
        self.add_narrative(element, model)
        # store element
        return element

    '''atributes:
        iso-date:2014-01-01

    tag:period-start'''

    def iati_organisations__iati_organisation__recipient_org_budget__period_start(self, element):
        model = self.get_model('RecipientOrgBudget')
        model.period_start = self.validate_date(element.attrib.get('iso-date'))

        # store element
        return element

    '''atributes:
        iso-date:2014-12-31

    tag:period-end'''

    def iati_organisations__iati_organisation__recipient_org_budget__period_end(self, element):
        model = self.get_model('RecipientOrgBudget')
        model.period_end = self.validate_date(element.attrib.get('iso-date'))
        # store element
        return element

    '''atributes:
        currency:USD
        value-date:2014-01-01

    tag:value'''

    def iati_organisations__iati_organisation__recipient_org_budget__value(self, element):
        model = self.get_model('RecipientOrgBudget')
        model.currency = self.get_or_none(codelist_models.Currency, code=self._get_currency_or_raise(element.attrib.get('currency')))
        model.value = element.text
        # store element
        return element

    '''atributes:
        ref:1234

    tag:budget-line'''

    def iati_organisations__iati_organisation__recipient_org_budget__budget_line(self, element):
        model = self.get_model('RecipientOrgBudget')
        budget_line = BudgetLine()
        budget_line.ref = element.attrib.get('ref')
        budget_line.parent = model
        self.register_model('RecipientOrgBudgetLine', budget_line)
        # store element
        return element

    '''atributes:
        currency:USD
        value-date:2014-01-01

    tag:value'''

    def iati_organisations__iati_organisation__recipient_org_budget__budget_line__value(self, element):
        model = self.get_model('RecipientOrgBudgetLine')
        model.currency = self.get_or_none(codelist_models.Currency, code=self._get_currency_or_raise(element.attrib.get('currency')))
        model.value = element.text
        model.value_date = self.validate_date(element.attrib.get('value-date'))
        # store element
        return element

    '''atributes:

    tag:narrative'''

    def iati_organisations__iati_organisation__recipient_org_budget__budget_line__narrative(self, element):
        model = self.get_model('RecipientOrgBudgetLine')
        self.add_narrative(element, model)
        # store element
        return element

    '''atributes:

    tag:recipient-country-budget'''

    def iati_organisations__iati_organisation__recipient_country_budget(self, element):
        model = self.get_model('Organisation')
        recipient_country_budget = RecipientCountryBudget()
        recipient_country_budget.organisation = model
        self.register_model('RecipientCountryBudget', recipient_country_budget)
        # store element
        return element

    '''atributes:
        code:AF

    tag:recipient-country'''

    def iati_organisations__iati_organisation__recipient_country_budget__recipient_country(self, element):
        model = self.get_model('RecipientCountryBudget')
        model.country = self.get_or_none(Country, code=element.attrib.get('code'))

        # store element
        return element

    '''atributes:
        iso-date:2014-01-01

    tag:period-start'''

    def iati_organisations__iati_organisation__recipient_country_budget__period_start(self, element):
        model = self.get_model('RecipientCountryBudget')
        model.period_start = self.validate_date(element.attrib.get('iso-date'))
        # store element
        return element

    '''atributes:
        iso-date:2014-12-31

    tag:period-end'''

    def iati_organisations__iati_organisation__recipient_country_budget__period_end(self, element):
        model = self.get_model('RecipientCountryBudget')
        model.period_end = self.validate_date(element.attrib.get('iso-date'))
        # store element
        return element

    '''atributes:
        currency:USD
        value-date:2014-01-01

    tag:value'''

    def iati_organisations__iati_organisation__recipient_country_budget__value(self, element):
        model = self.get_model('RecipientCountryBudget')
        model.currency = self.get_or_none(codelist_models.Currency, code=self._get_currency_or_raise(element.attrib.get('currency')))
        model.value = element.text
        # store element
        return element

    '''atributes:
        ref:1234

    tag:budget-line'''

    def iati_organisations__iati_organisation__recipient_country_budget__budget_line(self, element):
        model = self.get_model('RecipientCountryBudget')
        budget_line = BudgetLine()
        budget_line.ref = element.attrib.get('ref')
        budget_line.parent = model
        self.register_model('RecipientCountryBudgetLine',budget_line)
        # store element
        return element

    '''atributes:
        currency:USD
        value-date:2014-01-01

    tag:value'''

    def iati_organisations__iati_organisation__recipient_country_budget__budget_line__value(self, element):
        model = self.get_model('RecipientCountryBudgetLine')
        model.currency = self.get_or_none(codelist_models.Currency, code=self._get_currency_or_raise(element.attrib.get('currency')))
        model.value = element.text
        model.value_date = self.validate_date(element.attrib.get('value-date'))
        # store element
        return element

    '''atributes:

    tag:narrative'''

    def iati_organisations__iati_organisation__recipient_country_budget__budget_line__narrative(self, element):
        model = self.get_model('RecipientCountryBudgetLine')
        self.add_narrative(element, model)
        # store element
        return element

    '''atributes:
        format:application/vnd.oasis.opendocument.text
        url:http:www.example.org/docs/report_en.odt

    tag:document-link'''

    def iati_organisations__iati_organisation__document_link(self, element):
        model = self.get_model('Organisation')
        document_link = DocumentLink()
        document_link.organisation = model
        document_link.url = element.attrib.get('url')
        document_link.file_format = self.get_or_none(codelist_models.FileFormat, code=element.attrib.get('format'))
        self.register_model('DocumentLink',document_link)

        # store element
        return element

    '''atributes:

    tag:title'''

    def iati_organisations__iati_organisation__document_link__title(self, element):
        model = self.get_model('DocumentLink')
        document_link_title = DocumentLinkTitle()
        document_link_title.document_link = model
        self.register_model('DocumentLinkTitle',document_link_title)

        # store element
        return element

    '''atributes:

    tag:narrative'''

    def iati_organisations__iati_organisation__document_link__title__narrative(self, element):
        model = self.get_model('DocumentLinkTitle')
        self.add_narrative(element, model)
        # store element
        return element

    '''atributes:
        code:B01

    tag:category'''
    def iati_organisations__iati_organisation__document_link__category(self, element):
        model = self.get_model('DocumentLink')
        model.save()
        document_category = self.get_or_none(codelist_models.DocumentCategory, code=element.attrib.get('code'))
        model.categories.add(document_category)
        # store element
        return element

    '''atributes:
        code:en

    tag:language'''

    def iati_organisations__iati_organisation__document_link__language(self, element):
        model = self.get_model('DocumentLink')
        model.language = self.get_or_none(codelist_models.Language, code=element.attrib.get('code'))
        # store element
        return element

    '''atributes:
        code:AF

    tag:recipient-country'''

    def iati_organisations__iati_organisation__document_link__recipient_country(self, element):
        model = self.get_model('DocumentLink')
        country = self.get_or_none(Country, code=element.attrib.get('code'))
        model.recipient_countries.add(country)

        # store element
        return element
