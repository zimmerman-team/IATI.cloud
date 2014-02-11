# Django specific
from django.conf.urls import *

urlpatterns = patterns('',
    url('^v1/', include('api.v1.urls')),
    url('', include('api.v3.urls')),
)

