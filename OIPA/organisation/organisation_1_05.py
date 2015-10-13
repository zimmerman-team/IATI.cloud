import re

from organisation.organisation_2_01 import Parse as Parse_2_01
from iati import models
from models import Name, Narrative, RecipientOrgBudget, ReportingOrg, Organisation


_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[-\s]+')


class Parse(Parse_2_01):

    VERSION = '1.05'
    default_lang = 'en'
    organisation_identifier = ''
    name = None

    def __init__(self):
        super(Parse_2_01, self).__init__()
        self.name = None

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
        organisation.last_updated_datetime = self.validate_date(element.attrib.get('last_updated_datetime'))
        if '{http://www.w3.org/XML/1998/namespace}lang' in element.attrib:
            organisation.default_lang = element.attrib['{http://www.w3.org/XML/1998/namespace}lang']
        organisation.iati_version_id = self.cached_db_call_no_version(models.Version, self.VERSION, createNew=True)

        organisation.save()
        # add to reporting organisation and recipient_organisation
        RecipientOrgBudget.objects.filter(recipient_org_identifier=self.organisation_identifier).update(recipient_org=organisation)
        ReportingOrg.objects.filter(reporting_org_identifier=self.organisation_identifier).update(reporting_org=organisation)
        self.set_func_model(organisation)
        # store element
        return element

    '''atributes:

    tag:name
    found in https://raw.githubusercontent.com/IATI/IATI-Extra-Documentation/version-2.01/en/organisation-standard/organisation-standard-example-annotated.xml at line 11 iati_version =2.01'''

    def iati_organisations__iati_organisation__name(self, element):
        model = self.get_func_parent_model()
        if self.name == None:
            self.name = Name()
            self.name.organisation = model
            self.name.save()
        self.add_narrative(element, self.name)

        # store element
        return element

    def iati_organisations__iati_organisation__iati_identifier(self, element):
        pass
