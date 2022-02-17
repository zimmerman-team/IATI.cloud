from functools import lru_cache

import requests

# Original data source: https://codelists.codeforiati.org/api/
SOURCES = {
    "ActivityDateType": "https://codelists.codeforiati.org/api/json/en/ActivityDateType.json",
    "ActivityScope": "https://codelists.codeforiati.org/api/json/en/ActivityScope.json",
    "ActivityStatus": "https://codelists.codeforiati.org/api/json/en/ActivityStatus.json",
    "AidType": "https://codelists.codeforiati.org/api/json/en/AidType.json",
    "AidType-category": "https://codelists.codeforiati.org/api/json/en/AidType-category.json",
    "AidTypeVocabulary": "https://codelists.codeforiati.org/api/json/en/AidTypeVocabulary.json",
    "BudgetIdentifier": "https://codelists.codeforiati.org/api/json/en/BudgetIdentifier.json",
    "BudgetIdentifierSector": "https://codelists.codeforiati.org/api/json/en/BudgetIdentifierSector.json",
    "BudgetIdentifierSector-category": "https://codelists.codeforiati.org/api/json/en/BudgetIdentifierSector-category.json",  # NOQA: E501
    "BudgetIdentifierVocabulary": "https://codelists.codeforiati.org/api/json/en/BudgetIdentifierVocabulary.json",
    "BudgetNotProvided": "https://codelists.codeforiati.org/api/json/en/BudgetNotProvided.json",
    "BudgetStatus": "https://codelists.codeforiati.org/api/json/en/BudgetStatus.json",
    "BudgetType": "https://codelists.codeforiati.org/api/json/en/BudgetType.json",
    "CRSAddOtherFlags": "https://codelists.codeforiati.org/api/json/en/CRSAddOtherFlags.json",
    "CRSChannelCode": "https://codelists.codeforiati.org/api/json/en/CRSChannelCode.json",
    "CashandVoucherModalities": "https://codelists.codeforiati.org/api/json/en/CashandVoucherModalities.json",
    "CollaborationType": "https://codelists.codeforiati.org/api/json/en/CollaborationType.json",
    "ConditionType": "https://codelists.codeforiati.org/api/json/en/ConditionType.json",
    "ContactType": "https://codelists.codeforiati.org/api/json/en/ContactType.json",
    "Country": "https://codelists.codeforiati.org/api/json/en/Country.json",
    "Currency": "https://codelists.codeforiati.org/api/json/en/Currency.json",
    "DescriptionType": "https://codelists.codeforiati.org/api/json/en/DescriptionType.json",
    "DisbursementChannel": "https://codelists.codeforiati.org/api/json/en/DisbursementChannel.json",
    "DocumentCategory": "https://codelists.codeforiati.org/api/json/en/DocumentCategory.json",
    "DocumentCategory-category": "https://codelists.codeforiati.org/api/json/en/DocumentCategory-category.json",
    "EarmarkingCategory": "https://codelists.codeforiati.org/api/json/en/EarmarkingCategory.json",
    "EarmarkingModality": "https://codelists.codeforiati.org/api/json/en/EarmarkingModality.json",
    "FileFormat": "https://codelists.codeforiati.org/api/json/en/FileFormat.json",
    "FinanceType": "https://codelists.codeforiati.org/api/json/en/FinanceType.json",
    "FinanceType-category": "https://codelists.codeforiati.org/api/json/en/FinanceType-category.json",
    "FlowType": "https://codelists.codeforiati.org/api/json/en/FlowType.json",
    "GLIDENumber": "https://codelists.codeforiati.org/api/json/en/GLIDENumber.json",
    "GazetteerAgency": "https://codelists.codeforiati.org/api/json/en/GazetteerAgency.json",
    "GeographicExactness": "https://codelists.codeforiati.org/api/json/en/GeographicExactness.json",
    "GeographicLocationClass": "https://codelists.codeforiati.org/api/json/en/GeographicLocationClass.json",
    "GeographicLocationReach": "https://codelists.codeforiati.org/api/json/en/GeographicLocationReach.json",
    "GeographicVocabulary": "https://codelists.codeforiati.org/api/json/en/GeographicVocabulary.json",
    "GeographicalPrecision": "https://codelists.codeforiati.org/api/json/en/GeographicalPrecision.json",
    "HumanitarianGlobalClusters": "https://codelists.codeforiati.org/api/json/en/HumanitarianGlobalClusters.json",
    "HumanitarianPlan": "https://codelists.codeforiati.org/api/json/en/HumanitarianPlan.json",
    "HumanitarianScopeType": "https://codelists.codeforiati.org/api/json/en/HumanitarianScopeType.json",
    "HumanitarianScopeVocabulary": "https://codelists.codeforiati.org/api/json/en/HumanitarianScopeVocabulary.json",
    "IATIOrganisationIdentifier": "https://codelists.codeforiati.org/api/json/en/IATIOrganisationIdentifier.json",
    "IndicatorMeasure": "https://codelists.codeforiati.org/api/json/en/IndicatorMeasure.json",
    "IndicatorVocabulary": "https://codelists.codeforiati.org/api/json/en/IndicatorVocabulary.json",
    "Language": "https://codelists.codeforiati.org/api/json/en/Language.json",
    "LoanRepaymentPeriod": "https://codelists.codeforiati.org/api/json/en/LoanRepaymentPeriod.json",
    "LoanRepaymentType": "https://codelists.codeforiati.org/api/json/en/LoanRepaymentType.json",
    "LocationType": "https://codelists.codeforiati.org/api/json/en/LocationType.json",
    "LocationType-category": "https://codelists.codeforiati.org/api/json/en/LocationType-category.json",
    "OrganisationIdentifier": "https://codelists.codeforiati.org/api/json/en/OrganisationIdentifier.json",
    "OrganisationRegistrationAgency": "https://codelists.codeforiati.org/api/json/en/OrganisationRegistrationAgency.json",  # NOQA: E501
    "OrganisationRole": "https://codelists.codeforiati.org/api/json/en/OrganisationRole.json",
    "OrganisationType": "https://codelists.codeforiati.org/api/json/en/OrganisationType.json",
    "OtherIdentifierType": "https://codelists.codeforiati.org/api/json/en/OtherIdentifierType.json",
    "PolicyMarker": "https://codelists.codeforiati.org/api/json/en/PolicyMarker.json",
    "PolicyMarkerVocabulary": "https://codelists.codeforiati.org/api/json/en/PolicyMarkerVocabulary.json",
    "PolicySignificance": "https://codelists.codeforiati.org/api/json/en/PolicySignificance.json",
    "PublisherType": "https://codelists.codeforiati.org/api/json/en/PublisherType.json",
    "Region": "https://codelists.codeforiati.org/api/json/en/Region.json",
    "RegionM49": "https://codelists.codeforiati.org/api/json/en/RegionM49.json",
    "RegionVocabulary": "https://codelists.codeforiati.org/api/json/en/RegionVocabulary.json",
    "RelatedActivityType": "https://codelists.codeforiati.org/api/json/en/RelatedActivityType.json",
    "ReportingOrganisation": "https://codelists.codeforiati.org/api/json/en/ReportingOrganisation.json",
    "ResultType": "https://codelists.codeforiati.org/api/json/en/ResultType.json",
    "ResultVocabulary": "https://codelists.codeforiati.org/api/json/en/ResultVocabulary.json",
    "Sector": "https://codelists.codeforiati.org/api/json/en/Sector.json",
    "SectorCategory": "https://codelists.codeforiati.org/api/json/en/SectorCategory.json",
    "SectorGroup": "https://codelists.codeforiati.org/api/json/en/SectorGroup.json",
    "SectorVocabulary": "https://codelists.codeforiati.org/api/json/en/SectorVocabulary.json",
    "TagVocabulary": "https://codelists.codeforiati.org/api/json/en/TagVocabulary.json",
    "TiedStatus": "https://codelists.codeforiati.org/api/json/en/TiedStatus.json",
    "TransactionType": "https://codelists.codeforiati.org/api/json/en/TransactionType.json",
    "UNSDG-Goals": "https://codelists.codeforiati.org/api/json/en/UNSDG-Goals.json",
    "UNSDG-Indicators": "https://codelists.codeforiati.org/api/json/en/UNSDG-Indicators.json",
    "UNSDG-Targets": "https://codelists.codeforiati.org/api/json/en/UNSDG-Targets.json",
    "VerificationStatus": "https://codelists.codeforiati.org/api/json/en/VerificationStatus.json",
    "Version": "https://codelists.codeforiati.org/api/json/en/Version.json"
}


@lru_cache(maxsize=None)
class Codelists(object):
    """
    An object instantiating and containing the codelists
    """

    def __init__(self):
        self.codelists = {}
        self.read_codelists()

    def read_codelists(self):
        """
        Initialize the codelists by reading the listed json files and storing
        them in a dictionary.

        :return: None
        """
        for key, value in SOURCES.items():
            r = requests.get(value)
            data = r.json()['data']
            self.codelists[key] = data

    def get_value(self, codelist_name, code, key='code', tbr='name'):
        """
        Code can be a single code, '11', or a list of codes, [11, 12].
        If code is a list, stringify and retrieve the value for each, otherwise
        return the value for the single code..

        :param codelist_name: The name of the codelist
        :param key: The key to retrieve the value from, default is 'code'.
        :param code: The code within the codelist, can be string or list.
        :param tbr: the field to be retrieved, for example 'name' or 'description', default is 'name'.
        :return: The content of the codelist at the given code, or a list of those values if the 'code' is a list
        """
        try:
            codelist = self.codelists[codelist_name]
            ret = []
            for item in codelist:
                if type(code) is list:
                    for single_code in code:
                        if item[key] == str(single_code):  # Ensure code is string
                            ret.append(item[tbr])
                            continue
                else:
                    if item[key] == code:  # single codes are passed as string
                        return item[tbr]
            return ret
        except:  # NOQA
            return ['Value was not found in current codelists.']
