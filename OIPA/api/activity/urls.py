from django.conf.urls import url
import api.activity.views
import api.sector.views
from django.views.decorators.cache import cache_page

from django.conf import settings


urlpatterns = [
    url(r'^$',
        api.activity.views.ActivityList.as_view(),
        name='activity-list'),
    url(r'^aggregations/',
        cache_page(settings.API_CACHE_SECONDS)(api.activity.views.ActivityAggregations.as_view()),
        name='activity-aggregations'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/$',
        api.activity.views.ActivityDetail.as_view(),
        name='activity-detail'),

    url(r'^(?P<pk>[^@$&+,/:;=?]+)/transactions/$',
        api.activity.views.ActivityTransactionList.as_view(),
        name='activity-transactions'),

    url(r'^(?P<pk>[^@$&+,/:;=?]+)/transactions/(?P<id>[^@$&+,/:;=?]+)$',
        api.activity.views.ActivityTransactionDetail.as_view(),
        name='activity-transaction-detail'),

    url(r'^(?P<pk>[^@$&+,/:;=?]+)/provider-activity-tree/$',
        api.activity.views.ActivityProviderActivityTree.as_view(),
        name='provider-activity-tree'),
    ]
