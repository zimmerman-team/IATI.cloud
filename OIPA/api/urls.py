from django.conf.urls import patterns
from django.conf.urls import url
from django.conf.urls import include


urlpatterns = patterns(
    '',
    url('', include('api.activity.urls')),
    url('^v1/', include('api.v1.urls')),
    url('', include('api.v3.urls')),
)
