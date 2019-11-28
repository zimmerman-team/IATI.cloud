from api.activity.serializers import BudgetSerializer
from api.iati.references import BudgetReference as ElementReference
from solr.references import ConvertElementReference


class BudgetReference(ConvertElementReference, ElementReference):

    def __init__(self, budget=None):
        data = BudgetSerializer(instance=budget).data

        super().__init__(parent_element=None, data=data)
