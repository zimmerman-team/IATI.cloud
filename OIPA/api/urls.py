from django.conf.urls import patterns
from django.conf.urls import url
from django.conf.urls import include
from api import views


urlpatterns = patterns(
    '',
    url('^$', views.api_root, name='api-root'),
    url('activities', include('api.activity.urls')),
    url('regions', include('api.region.urls')),
    url('countries', include('api.country.urls')),
    url('cities', include('api.city.urls')),
    url('organisations', include('api.organisation.urls')),
    url('sectors', include('api.sector.urls')),
    url('^v1/', include('api.v1.urls')),
    url('', include('api.v3.urls')),
)
