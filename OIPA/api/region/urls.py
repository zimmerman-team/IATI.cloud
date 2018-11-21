from django.conf.urls import url

from api.region import views

app_name = 'api'
urlpatterns = [
    url(r'^$', views.RegionList.as_view(), name='region-list'),
    url(
        r'^(?P<pk>[A-Za-z0-9]+)/$',
        views.RegionDetail.as_view(),
        name='region-detail'
    ),
]
