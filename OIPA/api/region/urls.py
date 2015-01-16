from django.conf.urls import patterns, url
from api.region import views


urlpatterns = patterns(
    '',
    url(r'^$', views.RegionList.as_view(), name='region-list'),
    url(
        r'^/(?P<pk>[0-9]+)$',
        views.RegionDetail.as_view(),
        name='region-detail'
    ),
    url(
        r'^/(?P<pk>[0-9]+)/countries$',
        views.RegionCountries.as_view(),
        name='region-countries'
    ),
    url(
        r'^/(?P<pk>[0-9]+)/activities$',
        views.RegionActivities.as_view(),
        name='region-activities'
    ),
)
