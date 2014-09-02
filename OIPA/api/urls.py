# Django specific
from django.conf.urls import *
from views import debug

urlpatterns = patterns('',
    url('^v1/', include('api.v1.urls')),
    url('', include('api.dev.urls')),
    url('', include('api.v3.urls')),
)

