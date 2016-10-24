from django.conf.urls import url
from api.publisher import views


urlpatterns = [
    url(r'^$', views.PublisherList.as_view(), name='publisher-list'),
    url(
        r'^(?P<pk>[^@$&+,/:;=?]+)/$',
        views.PublisherDetail.as_view(),
        name='publisher-detail'
    ),
    url(
        r'^(?P<pk>[^@$&+,/:;=?]+)/admin-group/$',
        views.AdminGroupView.as_view(),
        name='publisher-admingroup-list'
    ),
    url(
        r'^(?P<pk>[^@$&+,/:;=?]+)/admin-group/(?P<id>[^@$&+,/:;=?]+)$',
        views.AdminGroupDetailView.as_view(),
        name='publisher-admingroup-detail'
    ),
]
