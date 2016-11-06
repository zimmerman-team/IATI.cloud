from django.conf.urls import url
from api.sector import views


urlpatterns = [
    url(r'^$', views.SectorList.as_view(), name='sector-list'),
    url(
        r'^(?P<pk>[^@$&+,/:;=?]+)/$',
        views.SectorDetail.as_view(),
        name='sector-detail'
    ),
]
