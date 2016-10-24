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
        views.OrganisationAdminGroupView.as_view(),
        name='publisher-admingroup-list'
    ),
    url(
        r'^(?P<pk>[^@$&+,/:;=?]+)/admin-group/(?P<id>[^@$&+,/:;=?]+)$',
        views.OrganisationAdminGroupDetailView.as_view(),
        name='publisher-admingroup-detail'
    ),
    url(
        r'^(?P<pk>[^@$&+,/:;=?]+)/group/$',
        views.OrganisationGroupView.as_view(),
        name='publisher-group-list'
    ),
    url(
        r'^(?P<pk>[^@$&+,/:;=?]+)/group/(?P<id>[^@$&+,/:;=?]+)$',
        views.OrganisationGroupDetailView.as_view(),
        name='publisher-group-detail'
    ),
]
