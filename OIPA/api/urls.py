from django.conf.urls import patterns
from django.conf.urls import url
from django.conf.urls import include
from api import views


urlpatterns = patterns(
    '',
    url(r'^$', views.welcome, name='api-root'),
    url(r'^activities', include('api.activity.urls')),
    url(r'^regions', include('api.region.urls')),
    url(r'^countries', include('api.country.urls')),
    url(r'^cities', include('api.city.urls')),
    url(r'^organisations', include('api.organisation.urls')),
    url(r'^sectors', include('api.sector.urls')),
    url(r'^transactions', include('api.transaction.urls',
        namespace='transactions')),
    url('^v1/', include('api.v1.urls')),
    url('', include('api.v3.urls')),
)
