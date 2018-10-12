from django.conf.urls import url

from api.unesco.views import SectorBudgets, TransactionBalanceAggregation

app_name = 'api'
urlpatterns = [
    url(r'^transaction-balance-aggregations',
        TransactionBalanceAggregation.as_view(),
        name='transaction-balance-aggregations'),
    url(r'^sector-budgets',
        SectorBudgets.as_view({'get': 'list'}),
        name='sector-budgets'),
]
