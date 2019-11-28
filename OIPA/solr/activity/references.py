from api.activity.serializers import ReportingOrganisationSerializer
from api.iati.references import ReportingOrgOrgReference as ElementReference
from solr.references import ConvertElementReference


class ReportingOrgReference(ConvertElementReference, ElementReference):

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
