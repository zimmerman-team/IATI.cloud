from django.conf.urls import url

from api.unesco.views import TransactionBalanceAggregation

app_name = 'api'
urlpatterns = [
    url(r'^transaction-balance-aggregations',
        TransactionBalanceAggregation.as_view(),
        name='transaction-balance-aggregation'),
]