# Django specific
from django.conf.urls import *

urlpatterns = patterns('',
    url('^v1/', include('API.v1.urls')),
    url('', include('API.v3.urls')),
)

