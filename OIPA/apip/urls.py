# Django specific
from django.conf.urls import *

urlpatterns = patterns('',
    url('^v1/', include('apip.v1.urls')),
    url('', include('apip.v3.urls')),
)

