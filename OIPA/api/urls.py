from django.conf.urls import patterns
from django.conf.urls import url
from django.conf.urls import include


urlpatterns = patterns(
    '',
    url('activities', include('api.activity.urls')),
    url('regions', include('api.region.urls')),
    url('country', include('api.country.urls')),
    url('city', include('api.city.urls')),
    url('^v1/', include('api.v1.urls')),
    url('', include('api.v3.urls')),
)
