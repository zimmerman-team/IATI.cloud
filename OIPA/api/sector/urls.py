from django.conf.urls import patterns, url
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
