import re

from iati_organisation.organisation_2_01 import Parse as Parse_2_01
from iati import models
from models import OrganisationName, OrganisationNarrative, RecipientOrgBudget, OrganisationReportingOrganisation, Organisation
from iati_codelists import models as codelist_models


_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[-\s]+')


class Parse(Parse_2_01):

    VERSION = '1.05' # version of iati standard
    organisation_identifier = None

    def __init__(self, *args, **kwargs):
        super(Parse_2_01, self).__init__(*args, **kwargs)
        self.VERSION = codelist_models.Version.objects.get(code='1.05')


    def iati_organisations__iati_organisation(self, element):
        id = self._normalize(element.xpath('iati-identifier/text()')[0])
        last_updated_datetime = self.validate_date(element.attrib.get('last-updated-datetime'))
        default_lang = element.attrib.get('{http://www.w3.org/XML/1998/namespace}lang')
        default_currency = self.get_or_none(codelist_models.Currency, code=element.attrib.get('default-currency'))

        if not id:
            raise self.RequiredFieldError("id", "organisation: must contain iati-identifier")

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

        self.register_model('Organisation', organisation)
        return element

    def iati_organisations__iati_organisation__iati_identifier(self, element):
        # already set in iati_organisation
        pass

    def iati_organisations__iati_organisation__name(self, element):
        super(Parse, self).iati_organisations__iati_organisation__name(element)
        name = self.get_model('Name')

        if element.text:
            self.add_narrative(element, name)

        return element

