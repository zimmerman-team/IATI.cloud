from api.iati.references import ResultReference as ElementReference
from solr.references import ConvertElementReference
from solr.result.serializers import ResultSerializer


class ResultReference(ConvertElementReference, ElementReference):

    def __init__(self, result=None):
        data = ResultSerializer(instance=result).data

        super().__init__(parent_element=None, data=data)
