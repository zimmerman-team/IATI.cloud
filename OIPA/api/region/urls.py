from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
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
urlpatterns = format_suffix_patterns(
    urlpatterns, allowed=['json', 'api', 'xml', 'csv'])
