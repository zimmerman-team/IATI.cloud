from api.activity.serializers import (
    ActivityDateSerializer, ActivityDefaultAidTypeSerializer,
    ActivityPolicyMarkerSerializer, ActivityTagSerializer, CodelistSerializer,
    ConditionsSerializer, ContactInfoSerializer, CountryBudgetItemsSerializer,
    CrsAddSerializer, DescriptionSerializer, DocumentLinkSerializer,
    FssSerializer, HumanitarianScopeSerializer, LegacyDataSerializer,
    OtherIdentifierSerializer, ParticipatingOrganisationSerializer,
    PlannedDisbursementSerializer, RelatedActivitySerializer,
    ReportingOrganisationSerializer, TitleSerializer
)
from api.iati.references import \
    ActivityDateReference as BaseActivityDateReference
from api.iati.references import \
    ActivityScopeReference as BaseActivityScopeReference
from api.iati.references import \
    ActivityStatusReference as BaseActivityStatusReference
from api.iati.references import \
    CapitalSpendReference as BaseCapitalSpendReference
from api.iati.references import \
    CollaborationTypeReference as BaseCollaborationTypeReference
from api.iati.references import ConditionsReference as BaseConditionsReference
from api.iati.references import \
    ContactInfoReference as BaseContactInfoReference
from api.iati.references import \
    CountryBudgetItemsReference as BaseCountryBudgetItemsReference
from api.iati.references import CrsAddReference as BaseCrsAddReference
from api.iati.references import \
    DefaultAidTypeReference as BaseDefaultAidTypeReference
from api.iati.references import \
    DefaultFinanceTypeReference as BaseDefaultFinanceTypeReference
from api.iati.references import \
    DefaultFlowTypeReference as BaseDefaultFlowTypeReference
from api.iati.references import \
    DefaultTiedStatusReference as BaseDefaultTiedStatusReference
from api.iati.references import \
    DescriptionReference as BaseDescriptionReference
from api.iati.references import \
    DocumentLinkReference as BaseDocumentLinkReference
from api.iati.references import FssReference as BaseFssReference
from api.iati.references import \
    HumanitarianScopeReference as BaseHumanitarianScopeReference
from api.iati.references import LegacyDataReference as BaseLegacyDataReference
from api.iati.references import LocationReference as BaseLocationReference
from api.iati.references import \
    OtherIdentifierReference as BaseOtherIdentifierReference
from api.iati.references import \
    ParticipatingOrgReference as BaseParticipatingOrgReference
from api.iati.references import \
    PlannedDisbursementReference as BasePlannedDisbursementReference
from api.iati.references import \
    PolicyMarkerReference as BasePolicyMarkerReference
from api.iati.references import \
    RecipientCountryReference as BaseRecipientCountryReference
from api.iati.references import \
    RecipientRegionReference as BaseRecipientRegionReference
from api.iati.references import \
    RelatedActivityReference as BaseRelatedActivityReference
from api.iati.references import \
    ReportingOrgOrgReference as BaseReportingOrgElementReference
from api.iati.references import SectorReference as BaseSectorReference
from api.iati.references import TagReference as BaseTagReference
from api.iati.references import TitleReference as BaseTitleReference
from solr.activity.serializers import (
    ActivityRecipientRegionSerializer, ActivitySectorSerializer,
    LocationSerializer, RecipientCountrySerializer
)
from solr.references import ConvertElementReference


class ReportingOrgReference(ConvertElementReference,
                            BaseReportingOrgElementReference):

    def __init__(self, reporting_org=None):
        data = ReportingOrganisationSerializer(
            instance=reporting_org,
            fields=['id', 'ref', 'type', 'secondary_reporter', 'narrative']
        ).data

        super().__init__(parent_element=None, data=data)


class TitleReference(ConvertElementReference, BaseTitleReference):

    def __init__(self, title=None):
        data = TitleSerializer(instance=title).data

        super().__init__(parent_element=None, data=data)


class DescriptionReference(ConvertElementReference, BaseDescriptionReference):

    def __init__(self, description=None):
        data = DescriptionSerializer(instance=description).data

        super().__init__(parent_element=None, data=data)


class ParticipatingOrgReference(ConvertElementReference,
                                BaseParticipatingOrgReference):

    def __init__(self, participating_org=None):
        data = ParticipatingOrganisationSerializer(
            instance=participating_org
        ).data

        super().__init__(parent_element=None, data=data)


class OtherIdentifierReference(ConvertElementReference,
                               BaseOtherIdentifierReference):

    def __init__(self, other_identifier=None):
        data = OtherIdentifierSerializer(
            instance=other_identifier
        ).data

        super().__init__(parent_element=None, data=data)


class ActivityStatusReference(ConvertElementReference,
                              BaseActivityStatusReference):

    def __init__(self, activity_status=None):
        data = CodelistSerializer(
            instance=activity_status
        ).data

        super().__init__(parent_element=None, data=data)


class ActivityDateReference(ConvertElementReference,
                            BaseActivityDateReference):

    def __init__(self, activity_date=None):
        data = ActivityDateSerializer(
            instance=activity_date
        ).data

        super().__init__(parent_element=None, data=data)


class ContactInfoReference(ConvertElementReference,
                           BaseContactInfoReference):

    def __init__(self, contact_info=None):
        data = ContactInfoSerializer(
            instance=contact_info
        ).data

        super().__init__(parent_element=None, data=data)


class ActivityScopeReference(ConvertElementReference,
                             BaseActivityScopeReference):

    def __init__(self, activity_scope=None):
        data = CodelistSerializer(
            instance=activity_scope
        ).data

        super().__init__(parent_element=None, data=data)


class RecipientCountryReference(ConvertElementReference,
                                BaseRecipientCountryReference):

    def __init__(self, recipient_country=None):
        data = RecipientCountrySerializer(
            instance=recipient_country
        ).data

        super().__init__(parent_element=None, data=data)


class RecipientRegionReference(ConvertElementReference,
                               BaseRecipientRegionReference):

    def __init__(self, recipient_region=None):
        data = ActivityRecipientRegionSerializer(
            instance=recipient_region
        ).data

        super().__init__(parent_element=None, data=data)


class LocationReference(ConvertElementReference, BaseLocationReference):

    def __init__(self, location=None):
        data = LocationSerializer(
            instance=location
        ).data

        super().__init__(parent_element=None, data=data)


class SectorReference(ConvertElementReference, BaseSectorReference):

    def __init__(self, sector=None):
        data = ActivitySectorSerializer(
            instance=sector
        ).data

        super().__init__(parent_element=None, data=data)


class TagReference(ConvertElementReference, BaseTagReference):

    def __init__(self, tag=None):
        data = ActivityTagSerializer(
            instance=tag
        ).data

        super().__init__(parent_element=None, data=data)


class CountryBudgetItemsReference(ConvertElementReference,
                                  BaseCountryBudgetItemsReference):

    def __init__(self, country_budget_items=None):
        data = CountryBudgetItemsSerializer(
            instance=country_budget_items
        ).data

        super().__init__(parent_element=None, data=data)


class PolicyMarkerReference(ConvertElementReference,
                            BasePolicyMarkerReference):

    def __init__(self, policy_marker=None):
        data = ActivityPolicyMarkerSerializer(
            instance=policy_marker
        ).data

        super().__init__(parent_element=None, data=data)


class HumanitarianScopeReference(ConvertElementReference,
                                 BaseHumanitarianScopeReference):

    def __init__(self, humanitarian_scope=None):
        data = HumanitarianScopeSerializer(
            instance=humanitarian_scope
        ).data

        super().__init__(parent_element=None, data=data)


class CollaborationTypeReference(ConvertElementReference,
                                 BaseCollaborationTypeReference):

    def __init__(self, collaboration_type=None):
        data = CodelistSerializer(
            instance=collaboration_type
        ).data

        super().__init__(parent_element=None, data=data)


class DefaultFlowTypeReference(ConvertElementReference,
                               BaseDefaultFlowTypeReference):

    def __init__(self, default_flow_type=None):
        data = CodelistSerializer(
            instance=default_flow_type
        ).data

        super().__init__(parent_element=None, data=data)


class DefaultFinanceTypeReference(ConvertElementReference,
                                  BaseDefaultFinanceTypeReference):

    def __init__(self, default_finance_type=None):
        data = CodelistSerializer(
            instance=default_finance_type
        ).data

        super().__init__(parent_element=None, data=data)


class DefaultAidTypeReference(ConvertElementReference,
                              BaseDefaultAidTypeReference):

    def __init__(self, default_aid_type=None):
        data = ActivityDefaultAidTypeSerializer(
            instance=default_aid_type
        ).data

        super().__init__(parent_element=None, data=data)


class DefaultTiedStatusReference(ConvertElementReference,
                                 BaseDefaultTiedStatusReference):

    def __init__(self, default_tied_status=None):
        data = CodelistSerializer(
            instance=default_tied_status
        ).data

        super().__init__(parent_element=None, data=data)


class PlannedDisbursementReference(ConvertElementReference,
                                   BasePlannedDisbursementReference):

    def __init__(self, planned_disbursement=None):
        data = PlannedDisbursementSerializer(
            instance=planned_disbursement
        ).data

        super().__init__(parent_element=None, data=data)


class CapitalSpendReference(ConvertElementReference,
                            BaseCapitalSpendReference):

    def __init__(self, capital_spend=None):
        data = capital_spend

        super().__init__(parent_element=None, data=data)


class DocumentLinkReference(ConvertElementReference,
                            BaseDocumentLinkReference):

    def __init__(self, document_link=None):
        data = DocumentLinkSerializer(
            instance=document_link,
            fields=[
                'format',
                'url',
                'categories',
                'languages',
                'title',
                'document_date',
                'description'
            ]
        ).data

        super().__init__(parent_element=None, data=data)


class RelatedActivityReference(ConvertElementReference,
                               BaseRelatedActivityReference):

    def __init__(self, related_activity=None):
        data = RelatedActivitySerializer(
            instance=related_activity,
            fields=[
                'ref',
                'type'
            ]
        ).data

        super().__init__(parent_element=None, data=data)


class LegacyDataReference(ConvertElementReference, BaseLegacyDataReference):

    def __init__(self, legacy_data=None):
        data = LegacyDataSerializer(
            instance=legacy_data
        ).data

        super().__init__(parent_element=None, data=data)


class ConditionsReference(ConvertElementReference, BaseConditionsReference):

    def __init__(self, conditions=None):
        data = ConditionsSerializer(
            instance=conditions
        ).data

        super().__init__(parent_element=None, data=data)


class CrsAddReference(ConvertElementReference, BaseCrsAddReference):

    def __init__(self, crs_add=None):
        data = CrsAddSerializer(
            instance=crs_add
        ).data

        super().__init__(parent_element=None, data=data)


class FssReference(ConvertElementReference, BaseFssReference):

    def __init__(self, fss=None):
        data = FssSerializer(
            instance=fss
        ).data

        super().__init__(parent_element=None, data=data)
