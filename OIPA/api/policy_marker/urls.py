from django.conf.urls import patterns, url
from api.policy_marker import views


urlpatterns = patterns(
    '',
    url(r'^$', views.PolicyMarkerList.as_view(), name='policy-marker-list'),
   
)
