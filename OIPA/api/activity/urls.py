from django.conf.urls import patterns, url
import views


urlpatterns = patterns(
    '',
    url(r'^activities/$', views.ActivityList.as_view(), name='activity-list'),
    url(
        r'^activities/(?P<pk>[^@$&+,/:;=?]+)/$',
        views.ActivityDetail.as_view(),
        name='activity-detail'
    ),
)
