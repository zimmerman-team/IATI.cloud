from django.conf.urls import patterns
from django.conf.urls import url
from api.transaction import views


urlpatterns = patterns(
    '',
    url(r'^$', views.TransactionList.as_view(), name='transaction-list'),
    url(r'^(?P<id>\d+)$', views.TransactionDetail.as_view(),
        name='transaction-detail'),
)
