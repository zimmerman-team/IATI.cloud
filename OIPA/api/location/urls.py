from django.conf.urls import url
import api.location.views

app_name = 'api'
urlpatterns = [
    url(r'^$',
        api.location.views.LocationList.as_view(),
        name='location-list'),
    url(r'^(?P<pk>[0-9]+)/$',
        api.location.views.LocationDetail.as_view(),
        name='location-detail'),
]
