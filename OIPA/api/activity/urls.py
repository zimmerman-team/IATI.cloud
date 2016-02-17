from django.conf.urls import url
import api.activity.views
import api.sector.views


urlpatterns = [
    url(r'^$',
        api.activity.views.ActivityList.as_view(),
        name='activity-list'),
    url(r'^aggregations/',
        api.activity.views.ActivityAggregations.as_view(),
        name='activity-aggregations'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/$',
        api.activity.views.ActivityDetail.as_view(),
        name='activity-detail'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/transactions/',
        api.activity.views.ActivityTransactions.as_view(),
        name='activity-transactions'),
]
