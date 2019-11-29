from api.activity.serializers import (
    ActivityDateSerializer, CodelistSerializer, ContactInfoSerializer,
    DescriptionSerializer, OtherIdentifierSerializer,
    ParticipatingOrganisationSerializer, ReportingOrganisationSerializer,
    TitleSerializer
)
from api.iati.references import \
    ActivityDateReference as BaseActivityDateReference
from api.iati.references import \
    ActivityStatusReference as BaseActivityStatusReference
from api.iati.references import \
    ContactInfoReference as BaseContactInfoReference
from api.iati.references import \
    DescriptionReference as BaseDescriptionReference
from api.iati.references import \
    OtherIdentifierReference as BaseOtherIdentifierReference
from api.iati.references import \
    ParticipatingOrgReference as BaseParticipatingOrgReference
from api.iati.references import \
    ReportingOrgOrgReference as BaseReportingOrgElementReference
from api.iati.references import TitleReference as BaseTitleReference
from solr.references import ConvertElementReference


class ReportingOrgReference(ConvertElementReference,
                            BaseReportingOrgElementReference):

    def __init__(self, reporting_org=None):
        data = ReportingOrganisationSerializer(
            instance=reporting_org,
            fields=[
                'id',
                'ref',
                'type',
                'secondary_reporter',
                'narratives'
            ]
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
