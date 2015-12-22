from django.conf.urls import url
from api.policy_marker import views


urlpatterns = [
    url(r'^$', views.PolicyMarkerList.as_view(), name='policy-marker-list'),
]
