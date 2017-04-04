from django.conf.urls import url
from api.transaction.views import TransactionList
from api.transaction.views import TransactionDetail
from api.transaction.views import TransactionAggregation
from api.transaction.views import TransactionSectorList, TransactionSectorDetail
from django.views.decorators.cache import cache_page
from OIPA.production_settings import API_CACHE_SECONDS


urlpatterns = [
    url(r'^$',
        TransactionList.as_view(),
        name='transaction-list'),
    url(r'^(?P<pk>\d+)/$',
        TransactionDetail.as_view(),
        name='transaction-detail'),
    url(r'^(?P<pk>\d+)/sectors/$',
        TransactionSectorList.as_view(),
        name='transaction-sectors'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/sectors/(?P<id>[^@$&+,/:;=?]+)$',
        TransactionSectorDetail.as_view(),
        name='activity-sectors-detail'),
    url(r'^aggregations/',
        cache_page(API_CACHE_SECONDS)(TransactionAggregation.as_view()),
        name='activity-aggregations')
]
