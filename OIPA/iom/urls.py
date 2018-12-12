from django.conf.urls import url

import api.activity.views
import iom.views


urlpatterns = [
    url(r'^activity-list/',
        iom.views.ActivityList.as_view(),
        name='activity-list'),
]
