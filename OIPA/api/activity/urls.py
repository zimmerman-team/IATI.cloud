from django.conf.urls import patterns, url
from api.activity import views


urlpatterns = patterns(
    '',
    url(r'^/$', views.ActivityList.as_view(), name='activity-list'),
    url(
        r'^/(?P<pk>[^@$&+,/:;=?]+)/$',
        views.ActivityDetail.as_view(),
        name='activity-detail'
    ),
)
