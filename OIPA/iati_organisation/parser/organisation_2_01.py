from iati_organisation.parser.organisation_2_02 import Parse as IATI_202_Parser

from iati_codelists import models as codelist_models

from iati_organisation.models import (
    Organisation,
    OrganisationName,
    OrganisationReportingOrganisation,
    TotalBudget,
    OrganisationNarrative,
    RecipientOrgBudget,
    RecipientCountryBudget,
    OrganisationDocumentLink,
    DocumentLinkTitle)

from geodata.models import Country
from iati_organisation.parser import post_save
from iati.parser.exceptions import *


class Parse(IATI_202_Parser):
    
    organisation_identifier = ''

    def __init__(self, *args, **kwargs):
        super(Parse, self).__init__(*args, **kwargs)
        self.VERSION = '2.01'
