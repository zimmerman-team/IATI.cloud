from api.activity.serializers import (
    DescriptionSerializer, ParticipatingOrganisationSerializer,
    ReportingOrganisationSerializer, TitleSerializer
)
from api.iati.references import \
    DescriptionReference as BaseDescriptionReference
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
