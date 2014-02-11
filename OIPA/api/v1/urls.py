# Django specific
from django.conf.urls import *


urlpatterns = patterns('api.v1.views',
    url('^$', 'documentation_view'),
)