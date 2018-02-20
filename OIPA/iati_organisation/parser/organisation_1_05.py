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

    organisation_identifier = None

    def __init__(self, *args, **kwargs):
        super(Parse_2_01, self).__init__(*args, **kwargs)
        self.VERSION = '1.05'

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

        # check if names exist, if so remove and add all new ones + set primary_name

        if element.text:
            self.add_narrative(element, name)
            organisation = self.get_model('Organisation')
            organisation.primary_name = element.text

        return element

    def iati_organisations__iati_organisation__reporting_org(self, element):

        # reporting_org = element.xpath('reporting-org/@ref')

        super(Parse, self).iati_organisations__iati_organisation__reporting_org(element)

        # check if name element exists, If not and no org and org has no name, add
        # this as org name + primary name

        organisation_reporting_organisation = self.get_model('OrganisationReportingOrganisation')

        if element.text:
            organisation_reporting_organisation.primary_name = element.text
            self.add_narrative(element, organisation_reporting_organisation)

        activity_reporting_organisation = self.get_model('ActivityReportingOrganisation')

        if element.text:
            self.add_narrative(element, activity_reporting_organisation)

            # add org narrative if it doesnt exist yet
            ref = element.attrib.get('ref')
            organisation = self.get_or_none(models.Organisation, organisation_identifier=ref)

            if organisation.name.narratives.count() == 0:
                organisation.primary_name = element.text
                self.add_narrative(element, organisation.name, is_organisation_narrative=True)
                organisation.save()

        return element
