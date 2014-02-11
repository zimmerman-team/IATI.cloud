# Django specific
from django.conf.urls import *


urlpatterns = patterns('apip.v1.views',
    url('^$', 'documentation_view'),
)