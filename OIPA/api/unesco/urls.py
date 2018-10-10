from django.conf.urls import url

from api.unesco.views import (
    TransactionBalanceAggregation,
    SectorBudgetAggregations
)

app_name = 'api'
urlpatterns = [
    url(r'^transaction-balance-aggregations',
        TransactionBalanceAggregation.as_view(),
        name='transaction-balance-aggregations'),
    url(r'^sector-budgets',
        SectorBudgetAggregations.as_view({'get': 'list'}),
        name='sector-budgets'),
]
