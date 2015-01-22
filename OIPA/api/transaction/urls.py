from django.conf.urls import patterns
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from api.transaction.views import TransactionList
from api.transaction.views import TransactionDetail


urlpatterns = patterns(
    '',
    url(r'^$', TransactionList.as_view(), name='list'),
    url(r'^/(?P<pk>\d+)$', TransactionDetail.as_view(), name='detail'),
)
urlpatterns = format_suffix_patterns(
    urlpatterns, allowed=['json', 'api', 'xml', 'csv'])
