import re

from iati_organisation.organisation_2_01 import Parse as Parse_2_01
from iati import models
from models import Name, Narrative, RecipientOrgBudget, ReportingOrg, Organisation
from iati_codelists import models as codelist_models


_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[-\s]+')


class Parse(Parse_2_01):


    default_lang = 'en'
    organisation_identifier = ''
    name = None

    def __init__(self):
        super(Parse_2_01, self).__init__()
        self.VERSION = codelist_models.Version.objects.get(code='1.05')
        self.name = None

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
        narrative = Narrative()
        lang = self.default_lang
        if '{http://www.w3.org/XML/1998/namespace}lang' in element.attrib:
            lang = element.attrib['{http://www.w3.org/XML/1998/namespace}lang']
        narrative.language = language
        narrative.content = element.text
        narrative.organisation_identifier = self.organisation_identifier
        narrative.parent_object = parent
        # TODO: handle this differently (also: breaks tests)
        register_name = parent.__class__.__name__ + "Narrative"
        self.register_model(register_name, narrative)

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
        organisation.organisation_identifier = element.xpath('iati-identifier/text()')[0]
        self.organisation_identifier = organisation.organisation_identifier
        organisation.code = self.organisation_identifier
        organisation.last_updated_datetime = self.validate_date(element.attrib.get('last-updated-datetime'))
        if '{http://www.w3.org/XML/1998/namespace}lang' in element.attrib:
            organisation.default_lang =  self.get_or_none(codelist_models.Language,code=element.attrib['{http://www.w3.org/XML/1998/namespace}lang'])
        organisation.iati_version_id = self.VERSION
        organisation.default_currency = self.get_or_none(codelist_models.Currency,code=element.attrib.get('default-currency'))
        organisation.save()
        # add to reporting organisation and recipient_organisation
        RecipientOrgBudget.objects.filter(recipient_org_identifier=self.organisation_identifier).update(recipient_org=organisation)
        ReportingOrg.objects.filter(reporting_org_identifier=self.organisation_identifier).update(reporting_org=organisation)
        self.register_model('Organisation', organisation)
        # store element
        return element

    '''atributes:

    tag:name
    found in https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml at line 11 iati_version =2.01'''

    def iati_organisations__iati_organisation__name(self, element):
        model = self.get_model('Organisation')
        if self.name == None:
            self.name = Name()
            self.name.organisation = model
            self.register_model('Name',self.name)
        self.add_narrative(element, self.name)

        # store element
        return element

    def iati_organisations__iati_organisation__iati_identifier(self, element):
        pass
