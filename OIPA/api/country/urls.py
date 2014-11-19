from django.conf.urls import patterns, url
from api.country import views


urlpatterns = patterns(
    '',
    url(r'^/$', views.CountryList.as_view(), name='country-list'),
    url(
        r'^/(?P<pk>[A-Za-z]+)/$',
        views.CountryDetail.as_view(),
        name='country-detail'
    ),
)
