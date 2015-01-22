from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from api.sector import views


urlpatterns = patterns(
    '',
    url(r'^$', views.SectorList.as_view(), name='sector-list'),
    url(
        r'^/(?P<pk>[0-9]+)$',
        views.SectorDetail.as_view(),
        name='sector-detail'
    ),
    url(
        r'^/(?P<pk>[0-9]+)/activities$',
        views.SectorActivities.as_view(),
        name='sector-activities'
    ),
)
urlpatterns = format_suffix_patterns(
    urlpatterns, allowed=['json', 'api', 'xml', 'csv'])
