from django.conf.urls import url

from api.region import views

app_name = 'api'
urlpatterns = [
    url(r'^$', views.RegionList.as_view(), name='region-list'),
    url(
        r'^(?P<code>[^@$&+,/:;=?]+)/$',
        views.RegionDetail.as_view(),
        name='region-detail'
    ),
]
