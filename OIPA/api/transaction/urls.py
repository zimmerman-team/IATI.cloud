from django.conf.urls import url
from api.transaction.views import TransactionList
from api.transaction.views import TransactionDetail


urlpatterns = [
    url(r'^$', TransactionList.as_view(), name='list'),
    url(r'^(?P<pk>\d+)/$', TransactionDetail.as_view(), name='detail'),
]
