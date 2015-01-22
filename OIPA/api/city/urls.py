from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from api.city import views


urlpatterns = patterns(
    '',
    url(r'^$', views.CityList.as_view(), name='city-list'),
    url(
        r'^/(?P<pk>[0-9]+)$',
        views.CityDetail.as_view(),
        name='city-detail'
    ),
)
urlpatterns = format_suffix_patterns(
    urlpatterns, allowed=['json', 'api', 'xml', 'csv'])
