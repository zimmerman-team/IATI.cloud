from django.conf.urls import url
from api.city import views


urlpatterns = [
    url(r'^$', views.CityList.as_view(), name='city-list'),
    url(
        r'^(?P<pk>[0-9]+)/$',
        views.CityDetail.as_view(),
        name='city-detail'
    ),
]
