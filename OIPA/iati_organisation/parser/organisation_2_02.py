from iati.parser.iati_parser import IatiParser
from iati_codelists import models as codelist_models

from iati_organisation.models import (
    Organisation,
    OrganisationName,
    OrganisationReportingOrganisation,
    TotalBudget,
    OrganisationNarrative,
    BudgetLine,
    RecipientOrgBudget,
    RecipientCountryBudget,
    DocumentLink,
    DocumentLinkTitle)

from geodata.models import Country
from iati_organisation.parser import post_save


class Parse(IatiParser):
    VERSION = '2.02'
    organisation_identifier = ''

    # TODO: remove this inheritance - 2015-12-10
    def __init__(self, *args, **kwargs):
        super(Parse, self).__init__(*args, **kwargs)

    def add_narrative(self, element, parent):
        default_lang = self.default_lang # set on activity (if set)
        lang = element.attrib.get('{http://www.w3.org/XML/1998/namespace}lang', default_lang)
        text = element.text

        language = self.get_or_none(codelist_models.Language, code=lang)

        if not parent:
            raise self.ParserError(
                "Unknown", 
                "Narrative", 
                "parent object must be passed")

        register_name = parent.__class__.__name__ + "Narrative"

        if not language:
            raise self.RequiredFieldError(
                register_name,
                "xml:lang",
                "must specify xml:lang on iati-activity or xml:lang on the element itself")
        if not text:
            raise self.RequiredFieldError(
                register_name,
                "text", 
                "empty narrative")

        narrative = OrganisationNarrative()
        narrative.language = language
        narrative.content = element.text
        narrative.related_object = parent
        narrative.organisation = self.get_model('Organisation')

        # TODO: handle this differently (also: breaks tests)
        self.register_model(register_name, narrative)

    def _get_currency_or_raise(self, currency):
        """
        get default currency if not available for currency-related fields
        """
        if not currency:
            currency = getattr(self.get_model('Organisation'), 'default_currency')
            if not currency: raise self.RequiredFieldError(
                "", 
                "currency", 
                "currency: currency is not set and default-currency is not set on activity as well")

        return currency

    def iati_organisations__iati_organisation(self, element):
        id = self._normalize(element.xpath('organisation-identifier/text()')[0])
        last_updated_datetime = self.validate_date(element.attrib.get('last-updated-datetime'))
        default_lang = element.attrib.get('{http://www.w3.org/XML/1998/namespace}lang')
        default_currency = self.get_or_none(codelist_models.Currency, code=element.attrib.get('default-currency'))

        if not id:
            raise self.RequiredFieldError(
                "", 
                "id", 
                "organisation: must contain organisation-identifier")

        old_organisation = self.get_or_none(Organisation, id=id)

        if old_organisation:
            old_organisation.delete()

        organisation = Organisation()
        organisation.id = id
        organisation.organisation_identifier = id
        organisation.last_updated_datetime = last_updated_datetime
        organisation.default_lang_id = default_lang
        organisation.iati_standard_version_id = self.VERSION
        organisation.default_currency = default_currency

        self.organisation_identifier = organisation.organisation_identifier
        self.default_currency = default_currency

        # for later reference
        self.default_lang = default_lang
        
        self.register_model('Organisation', organisation)

        return element

    def iati_organisations__iati_organisation__organisation_identifier(self, element):
        # already set in iati_organisation
        return element

    def iati_organisations__iati_organisation__name(self, element):
        name_list = self.get_model_list('OrganisationName')

        if name_list and len(name_list) > 0:
            raise self.ValidationError("name", "Duplicate names are not allowed")

        organisation = self.get_model('Organisation')

        name = OrganisationName()
        name.organisation = organisation

        self.register_model('OrganisationName', name)

        return element

    def iati_organisations__iati_organisation__name__narrative(self, element):
        model = self.get_model('OrganisationName')
        self.add_narrative(element, model)

        if element.text:

            organisation = self.get_model('Organisation')
            
            if organisation.primary_name:
                default_lang = self.default_lang # set on activity (if set)
                lang = element.attrib.get('{http://www.w3.org/XML/1998/namespace}lang', default_lang)
                if lang == 'en':
                    organisation.primary_name = element.text
            else:
                organisation.primary_name = element.text
        return element

    def iati_organisations__iati_organisation__reporting_org(self, element):
        model = self.get_model('Organisation')

        reporting_org = OrganisationReportingOrganisation()
        reporting_org.organisation = model
        reporting_org.reporting_org_identifier = element.attrib.get('ref')
        type_ref = element.attrib.get('type')
        if self.isInt(type_ref) and self.get_or_none(codelist_models.OrganisationType, code=type_ref) != None:
            org_type = self.get_or_none(codelist_models.OrganisationType, code=type_ref)
            reporting_org.org_type = org_type
        self.register_model('OrganisationReportingOrganisation', reporting_org)

        return element

    def iati_organisations__iati_organisation__reporting_org__narrative(self, element):
        """atributes:

        tag:narrative"""
        model = self.get_model('OrganisationReportingOrganisation')
        self.add_narrative(element, model)
        return element

    def iati_organisations__iati_organisation__total_budget(self, element):
        """atributes:

        tag:total-budget"""
        status = self.get_or_none(codelist_models.BudgetStatus, code=element.attrib.get('status')) 
        
        model = self.get_model('Organisation')
        total_budget = TotalBudget()
        total_budget.organisation = model

        if status:
            total_budget.status = status

        self.register_model('TotalBudget', total_budget)
        # store element
        return element

    def iati_organisations__iati_organisation__total_budget__period_start(self, element):
        """atributes:
        iso-date:2014-01-01

        tag:period-start"""
        model = self.get_model('TotalBudget')
        model.period_start = self.validate_date(element.attrib.get('iso-date'))

        # store element
        return element

    def iati_organisations__iati_organisation__total_budget__period_end(self, element):
        """atributes:
        iso-date:2014-12-31

        tag:period-end"""
        model = self.get_model('TotalBudget')
        model.period_end = self.validate_date(element.attrib.get('iso-date'))
        # store element
        return element

    def iati_organisations__iati_organisation__total_budget__value(self, element):
        """atributes:
        currency:USD
        value-date:2014-01-0

        tag:value"""
        model = self.get_model('TotalBudget')
        model.currency = self.get_or_none(codelist_models.Currency, code=self._get_currency_or_raise(element.attrib.get('currency')))
        model.value_date = self.validate_date(element.attrib.get('value-date'))
        model.value = element.text
        # store element
        return element

    def iati_organisations__iati_organisation__total_budget__budget_line(self, element):
        """atributes:
        ref:1234

        tag:budget-line"""
        model = self.get_model('TotalBudget')
        budget_line = BudgetLine()
        budget_line.ref = element.attrib.get('ref')
        budget_line.parent = model
        self.register_model('TotalBudgetLine', budget_line)
        # store element
        return element

    def iati_organisations__iati_organisation__total_budget__budget_line__value(self, element):
        """atributes:
        currency:USD
        value-date:2014-01-01

        tag:value"""
        model = self.get_model('TotalBudgetLine')
        model.currency = self.get_or_none(codelist_models.Currency, code=self._get_currency_or_raise(element.attrib.get('currency')))
        model.value = element.text
        model.value_date = self.validate_date(element.attrib.get('value-date'))
        # store element
        return element

    def iati_organisations__iati_organisation__total_budget__budget_line__narrative(self, element):
        """atributes:

        tag:narrative"""
        model = self.get_model('TotalBudgetLine')

        self.add_narrative(element, model)
        # store element
        return element

    def iati_organisations__iati_organisation__recipient_org_budget(self, element):
        """atributes:

        tag:recipient-org-budget"""
        status = self.get_or_none(codelist_models.BudgetStatus, code=element.attrib.get('status')) 

        model = self.get_model('Organisation')
        recipient_org_budget = RecipientOrgBudget()
        recipient_org_budget.organisation = model
        if status:
            recipient_org_budget.status = status
        self.register_model('RecipientOrgBudget', recipient_org_budget)
        # store element
        return element

    def iati_organisations__iati_organisation__recipient_org_budget__recipient_org(self, element):
        """atributes:
        ref:AA-ABC-1234567

        tag:recipient-org"""
        model = self.get_model('RecipientOrgBudget')
        model.recipient_org_identifier = element.attrib.get('ref')
        if Organisation.objects.filter(id=element.attrib.get('ref')).exists():
            model.recipient_org = Organisation.objects.get(pk=element.attrib.get('ref'))

        # store element
        return element

    def iati_organisations__iati_organisation__recipient_org_budget__recipient_org__narrative(self, element):
        """atributes:

        tag:narrative"""
        model = self.get_model('RecipientOrgBudget')
        self.add_narrative(element, model)
        # store element
        return element

    def iati_organisations__iati_organisation__recipient_org_budget__period_start(self, element):
        """atributes:
        iso-date:2014-01-01

        tag:period-start"""
        model = self.get_model('RecipientOrgBudget')
        model.period_start = self.validate_date(element.attrib.get('iso-date'))

        # store element
        return element

    def iati_organisations__iati_organisation__recipient_org_budget__period_end(self, element):
        """atributes:
        iso-date:2014-12-31

        tag:period-end"""
        model = self.get_model('RecipientOrgBudget')
        model.period_end = self.validate_date(element.attrib.get('iso-date'))
        # store element
        return element

    def iati_organisations__iati_organisation__recipient_org_budget__value(self, element):
        """atributes:
        currency:USD
        value-date:2014-01-01

        tag:value"""
        model = self.get_model('RecipientOrgBudget')
        model.currency = self.get_or_none(codelist_models.Currency, code=self._get_currency_or_raise(element.attrib.get('currency')))
        model.value = element.text
        # store element
        return element

    def iati_organisations__iati_organisation__recipient_org_budget__budget_line(self, element):
        """atributes:
        ref:1234

        tag:budget-line"""
        model = self.get_model('RecipientOrgBudget')
        budget_line = BudgetLine()
        budget_line.ref = element.attrib.get('ref')
        budget_line.parent = model
        self.register_model('RecipientOrgBudgetLine', budget_line)
        # store element
        return element

    def iati_organisations__iati_organisation__recipient_org_budget__budget_line__value(self, element):
        """atributes:
        currency:USD
        value-date:2014-01-01

        tag:value"""
        model = self.get_model('RecipientOrgBudgetLine')
        model.currency = self.get_or_none(codelist_models.Currency, code=self._get_currency_or_raise(element.attrib.get('currency')))
        model.value = element.text
        model.value_date = self.validate_date(element.attrib.get('value-date'))
        # store element
        return element

    def iati_organisations__iati_organisation__recipient_org_budget__budget_line__narrative(self, element):
        """atributes:

        tag:narrative"""
        model = self.get_model('RecipientOrgBudgetLine')
        self.add_narrative(element, model)
        # store element
        return element

    def iati_organisations__iati_organisation__recipient_country_budget(self, element):
        """atributes:

        tag:recipient-country-budget"""
        status = self.get_or_none(codelist_models.BudgetStatus, code=element.attrib.get('status')) 
        model = self.get_model('Organisation')
        recipient_country_budget = RecipientCountryBudget()
        recipient_country_budget.organisation = model
        if status:
            recipient_country_budget.status = status
        self.register_model('RecipientCountryBudget', recipient_country_budget)
        # store element
        return element

    def iati_organisations__iati_organisation__recipient_country_budget__recipient_country(self, element):
        """atributes:
        code:AF

        tag:recipient-country"""
        model = self.get_model('RecipientCountryBudget')
        model.country = self.get_or_none(Country, code=element.attrib.get('code'))

        # store element
        return element

    def iati_organisations__iati_organisation__recipient_country_budget__period_start(self, element):
        """atributes:
        iso-date:2014-01-01

        tag:period-start"""
        model = self.get_model('RecipientCountryBudget')
        model.period_start = self.validate_date(element.attrib.get('iso-date'))
        # store element
        return element

    def iati_organisations__iati_organisation__recipient_country_budget__period_end(self, element):
        """atributes:
        iso-date:2014-12-31

        tag:period-end"""
        model = self.get_model('RecipientCountryBudget')
        model.period_end = self.validate_date(element.attrib.get('iso-date'))
        # store element
        return element

    def iati_organisations__iati_organisation__recipient_country_budget__value(self, element):
        """atributes:
        currency:USD
        value-date:2014-01-01

        tag:value"""
        model = self.get_model('RecipientCountryBudget')
        model.currency = self.get_or_none(codelist_models.Currency, code=self._get_currency_or_raise(element.attrib.get('currency')))
        model.value = element.text
        # store element
        return element

    def iati_organisations__iati_organisation__recipient_country_budget__budget_line(self, element):
        """atributes:
        ref:1234

        tag:budget-line"""
        model = self.get_model('RecipientCountryBudget')
        budget_line = BudgetLine()
        budget_line.ref = element.attrib.get('ref')
        budget_line.parent = model
        self.register_model('RecipientCountryBudgetLine',budget_line)
        # store element
        return element

    def iati_organisations__iati_organisation__recipient_country_budget__budget_line__value(self, element):
        """atributes:
        currency:USD
        value-date:2014-01-01

        tag:value"""
        model = self.get_model('RecipientCountryBudgetLine')
        model.currency = self.get_or_none(codelist_models.Currency, code=self._get_currency_or_raise(element.attrib.get('currency')))
        model.value = element.text
        model.value_date = self.validate_date(element.attrib.get('value-date'))
        # store element
        return element

    def iati_organisations__iati_organisation__recipient_country_budget__budget_line__narrative(self, element):
        """atributes:

        tag:narrative"""
        model = self.get_model('RecipientCountryBudgetLine')
        self.add_narrative(element, model)
        # store element
        return element

    def iati_organisations__iati_organisation__recipient_region_budget(self, element):
        """atributes:

        tag:recipient-region-budget"""
        status = self.get_or_none(codelist_models.BudgetStatus, code=element.attrib.get('status')) 
        model = self.get_model('Organisation')
        recipient_region_budget = RecipientRegionBudget()
        recipient_region_budget.organisation = model
        if status:
            recipient_region_budget.status = status
        self.register_model('RecipientRegionBudget', recipient_region_budget)
        # store element
        return element

    def iati_organisations__iati_organisation__recipient_region_budget__recipient_region(self, element):
        """atributes:
        code:AF

        tag:recipient-region"""
        model = self.get_model('RecipientRegionBudget')
        model.region = self.get_or_none(Region, code=element.attrib.get('code'))

        vocabulary = self.get_or_none(vocabulary_models.RegionVocabulary, code=element.attrib.get('vocabulary', '1')) # TODO: make defaults more transparant, here: 'OECD-DAC default'
        vocabulary_uri = element.attrib.get('vocabulary-uri')

        if not vocabulary: 
            raise self.RequiredFieldError(
                "recipient-region-budget", 
                "recipient-region", 
                "invalid vocabulary")

        model.vocabulary = vocabulary
        model.vocabulary_uri = vocabulary_uri

        # store element
        return element

    def iati_organisations__iati_organisation__recipient_region_budget__period_start(self, element):
        """atributes:
        iso-date:2014-01-01

        tag:period-start"""
        model = self.get_model('RecipientRegionBudget')
        model.period_start = self.validate_date(element.attrib.get('iso-date'))
        # store element
        return element

    def iati_organisations__iati_organisation__recipient_region_budget__period_end(self, element):
        """atributes:
        iso-date:2014-12-31

        tag:period-end"""
        model = self.get_model('RecipientRegionBudget')
        model.period_end = self.validate_date(element.attrib.get('iso-date'))
        # store element
        return element

    def iati_organisations__iati_organisation__recipient_region_budget__value(self, element):
        """atributes:
        currency:USD
        value-date:2014-01-01

        tag:value"""
        model = self.get_model('RecipientRegionBudget')
        model.currency = self.get_or_none(codelist_models.Currency, code=self._get_currency_or_raise(element.attrib.get('currency')))
        model.value = element.text
        # store element
        return element

    def iati_organisations__iati_organisation__recipient_region_budget__budget_line(self, element):
        """atributes:
        ref:1234

        tag:budget-line"""
        model = self.get_model('RecipientRegionBudget')
        budget_line = BudgetLine()
        budget_line.ref = element.attrib.get('ref')
        budget_line.parent = model
        self.register_model('RecipientRegionBudgetLine',budget_line)
        # store element
        return element

    def iati_organisations__iati_organisation__recipient_region_budget__budget_line__value(self, element):
        """atributes:
        currency:USD
        value-date:2014-01-01

        tag:value"""
        model = self.get_model('RecipientRegionBudgetLine')
        model.currency = self.get_or_none(codelist_models.Currency, code=self._get_currency_or_raise(element.attrib.get('currency')))
        model.value = element.text
        model.value_date = self.validate_date(element.attrib.get('value-date'))
        # store element
        return element

    def iati_organisations__iati_organisation__recipient_region_budget__budget_line__narrative(self, element):
        """atributes:

        tag:narrative"""
        model = self.get_model('RecipientRegionBudgetLine')
        self.add_narrative(element, model)
        # store element
        return element

    def iati_organisations__iati_organisation__document_link(self, element):
        """atributes:
        format:application/vnd.oasis.opendocument.text
        url:http:www.example.org/docs/report_en.odt

        tag:document-link"""
        model = self.get_model('Organisation')
        document_link = DocumentLink()
        document_link.organisation = model
        document_link.url = element.attrib.get('url')
        document_link.file_format = self.get_or_none(codelist_models.FileFormat, code=element.attrib.get('format'))
        self.register_model('DocumentLink',document_link)

        # store element
        return element

    def iati_organisations__iati_organisation__document_link__title(self, element):
        """atributes:

        tag:title"""
        model = self.get_model('DocumentLink')
        document_link_title = DocumentLinkTitle()
        document_link_title.document_link = model
        self.register_model('DocumentLinkTitle',document_link_title)

        # store element
        return element

    def iati_organisations__iati_organisation__document_link__title__narrative(self, element):
        """atributes:

    tag:narrative"""
        model = self.get_model('DocumentLinkTitle')
        self.add_narrative(element, model)
        # store element
        return element

    def iati_organisations__iati_organisation__document_link__category(self, element):
        """atributes:
        code:B01

        tag:category"""
        model = self.get_model('DocumentLink')
        model.save()
        document_category = self.get_or_none(codelist_models.DocumentCategory, code=element.attrib.get('code'))
        model.categories.add(document_category)
        # store element
        return element

    def iati_organisations__iati_organisation__document_link__language(self, element):
        """atributes:
        code:en

        tag:language"""
        model = self.get_model('DocumentLink')
        model.language = self.get_or_none(codelist_models.Language, code=element.attrib.get('code'))
        # store element
        return element

    def iati_organisations__iati_organisation__document_link__recipient_country(self, element):
        """atributes:
        code:AF

        tag:recipient-country"""
        model = self.get_model('DocumentLink')
        country = self.get_or_none(Country, code=element.attrib.get('code'))
        model.recipient_countries.add(country)

        # store element
        return element

    def post_save_models(self):
        """Perform all actions that need to happen after a single activity's been parsed."""
        organisation = self.get_model('Organisation')

        if not organisation:
            return False

        post_save.set_activity_reporting_organisation(organisation)

    def post_save_file(self, xml_source):
        pass
