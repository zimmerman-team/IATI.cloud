from django.conf.urls import patterns, url
from api.country import views


urlpatterns = patterns(
    '',
    url(r'^$', views.CountryList.as_view(), name='country-list'),
    url(
        r'^(?P<pk>[A-Za-z]+)/$',
        views.CountryDetail.as_view(),
        name='country-detail'
    ),
    url(
        r'^(?P<pk>[A-Za-z]+)/activities/$',
        views.CountryActivities.as_view(),
        name='country-activities'
    ),
    url(
        r'^(?P<pk>[A-Za-z]+)/indicators/$',
        views.CountryIndicators.as_view(),
        name='country-indicators'
    ),
    url(
        r'^(?P<pk>[A-Za-z]+)/cities/$',
        views.CountryIndicators.as_view(),
        name='country-cities'
    ),
)
