# Django specific
from django.conf.urls import *


urlpatterns = patterns('API.v1.views',
    url('^$', 'documentation_view'),
)