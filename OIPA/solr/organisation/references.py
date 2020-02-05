from api.iati.references import \
    DocumentLinkOrgReference as BaseDocumentLinkOrgReference
from api.iati.references import NameOrgReference as BaseNameOrgReference
from api.iati.references import \
    RecipientCountryBudgetOrgReference as \
    BaseRecipientCountryBudgetOrgReference
from api.iati.references import \
    RecipientOrgBudgetOrgReference as BaseRecipientOrgBudgetOrgReference
from api.iati.references import \
    RecipientRegionBudgetOrgReference as BaseRecipientRegionBudgetOrgReference
from api.iati.references import \
    TotalBudgetOrgReference as BaseTotalBudgetOrgReference
from api.iati.references import \
    TotalExpenditureOrgReference as BaseTotalExpenditureOrgReference
from api.organisation.serializers import (
    OrganisationDocumentLinkSerializer, OrganisationNameSerializer,
    OrganisationRecipientOrgBudgetSerializer,
    OrganisationTotalBudgetSerializer, OrganisationTotalExpenditureSerializer
)
from solr.organisation.serializers import (
    OrganisationRecipientCountryBudgetSerializer,
    OrganisationRecipientRegionBudgetSerializer
)
from solr.references import ConvertElementReference


class NameOrgReference(ConvertElementReference, BaseNameOrgReference):

    def __init__(self, organisation_name=None):
        data = OrganisationNameSerializer(
            instance=organisation_name
        ).data

        super().__init__(parent_element=None, data=data)


class TotalBudgetOrgReference(ConvertElementReference,
                              BaseTotalBudgetOrgReference):

    def __init__(self, organisation_total_budget=None):
        data = OrganisationTotalBudgetSerializer(
            instance=organisation_total_budget
        ).data

        super().__init__(parent_element=None, data=data)


class RecipientOrgBudgetOrgReference(ConvertElementReference,
                                     BaseRecipientOrgBudgetOrgReference):

    def __init__(self, organisation_recipient_org_budget=None):
        data = OrganisationRecipientOrgBudgetSerializer(
            instance=organisation_recipient_org_budget
        ).data

        super().__init__(parent_element=None, data=data)


class RecipientRegionBudgetOrgReference(ConvertElementReference,
                                        BaseRecipientRegionBudgetOrgReference):

    def __init__(self, organisation_recipient_region_budget=None):
        data = OrganisationRecipientRegionBudgetSerializer(
            instance=organisation_recipient_region_budget
        ).data

        super().__init__(parent_element=None, data=data)


class RecipientCountryBudgetOrgReference(
    ConvertElementReference,
    BaseRecipientCountryBudgetOrgReference
):

    def __init__(self, organisation_recipient_country_budget=None):
        data = OrganisationRecipientCountryBudgetSerializer(
            instance=organisation_recipient_country_budget
        ).data

        super().__init__(parent_element=None, data=data)


class TotalExpenditureOrgReference(ConvertElementReference,
                                   BaseTotalExpenditureOrgReference):

    def __init__(self, organisation_total_expenditure=None):
        data = OrganisationTotalExpenditureSerializer(
            instance=organisation_total_expenditure
        ).data

        super().__init__(parent_element=None, data=data)


class DocumentLinkOrgReference(ConvertElementReference,
                               BaseDocumentLinkOrgReference):

    def __init__(self, organisation_document_link=None):
        data = OrganisationDocumentLinkSerializer(
            instance=organisation_document_link
        ).data

        super().__init__(parent_element=None, data=data)
