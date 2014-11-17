from django.conf.urls import patterns, url
from drf_api import views


urlpatterns = patterns(
    '',
    url('^activities/$', views.ActivityList.as_view(), name='activity-list'),
)
