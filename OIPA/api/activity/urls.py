from django.conf.urls import patterns, url
import views


urlpatterns = patterns(
    '',
    url('^activities/$', views.ActivityList.as_view(), name='activity-list'),
)
