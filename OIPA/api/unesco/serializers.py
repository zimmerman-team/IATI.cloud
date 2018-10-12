from rest_framework import serializers

from api.generics.serializers import DynamicFieldsModelSerializer
from unesco.models import TransactionBalance
from iati.models import Sector


class TransactionBalanceSerializer(DynamicFieldsModelSerializer):

    class Meta:
        model = TransactionBalance
        fields = (
            'total_budget',
            'total_expenditure',
            'cumulative_budget',
            'cumulative_expenditure',
        )


class SectorBudgetsSerializer(serializers.ModelSerializer):
    # TODO: test
    total_budget = serializers.SerializerMethodField()

    class Meta:
        model = Sector
        fields = ('code', 'name', 'total_budget')

    def get_total_budget(self, obj):
        result = list(
            filter(
                lambda x: x['sector'] == obj.code,
                self.context.get('view').budgets
            )
        )

        return result[0].get('total_budget')
