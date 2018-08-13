from api.generics.serializers import DynamicFieldsModelSerializer
from unesco.models import TransactionBalance


class TransactionBalanceSerializer(DynamicFieldsModelSerializer):

    class Meta:
        model = TransactionBalance
        fields = (
            'total_budget',
            'total_expenditure',
            'cumulative_budget',
            'cumulative_expenditure',
        )

