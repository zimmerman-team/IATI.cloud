import re
from lxml.builder import E

from iati_organisation.parser.organisation_2_01 import Parse as Parse_2_01
from iati import models
from iati_organisation.models import OrganisationName
from iati_organisation.models import OrganisationNarrative
from iati_organisation.models import RecipientOrgBudget
from iati_organisation.models import OrganisationReportingOrganisation
from iati_organisation.models import Organisation
from iati_codelists import models as codelist_models
from iati.parser.exceptions import *


class Parse(Parse_2_01):

    VERSION = '1.05' # version of iati standard
    organisation_identifier = None

    def __init__(self, *args, **kwargs):
        super(Parse_2_01, self).__init__(*args, **kwargs)
        self.VERSION = codelist_models.Version.objects.get(code='1.05')

    def iati_organisations__iati_organisation(self, element):

        org_id = element.xpath('iati-identifier/text()')[0]

        if not org_id:
            raise self.RequiredFieldError(
                "iati-identifier",
                "text", 
                "Unspecified.")

        # add as organisation-identifier to be able to use in super of this def
        element.append(E("organisation-identifier", org_id))
        super(Parse, self).iati_organisations__iati_organisation(element)

        return element

    def iati_organisations__iati_organisation__iati_identifier(self, element):
        # already set in iati_organisation
        pass

    def iati_organisations__iati_organisation__name(self, element):
        super(Parse, self).iati_organisations__iati_organisation__name(element)
        name = self.get_model('OrganisationName')

        if element.text:
            self.add_narrative(element, name)
            organisation = self.get_model('Organisation')
            organisation.primary_name = element.text

        return element

    def iati_organisations__iati_organisation__reporting_org(self, element):
        super(Parse, self).iati_organisations__iati_organisation__reporting_org(element)

        organisation_reporting_organisation = self.get_model('OrganisationReportingOrganisation')

        if element.text:
            organisation_reporting_organisation.primary_name = element.text
            self.add_narrative(element, organisation_reporting_organisation)

        return element


