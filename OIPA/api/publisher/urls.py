from django.conf.urls import url
from api.publisher import views


urlpatterns = [
    url(r'^$', views.PublisherList.as_view(), name='publisher-list'),
    url(
        r'^(?P<publisher_id>[^@$&+,/:;=?]+)/$',
        views.PublisherDetail.as_view(),
        name='publisher-detail'
    ),
    url(
        r'^(?P<publisher_id>[^@$&+,/:;=?]+)/admin-group/$',
        views.OrganisationAdminGroupView.as_view(),
        name='publisher-admingroup-list'
    ),
    url(
        r'^(?P<publisher_id>[^@$&+,/:;=?]+)/admin-group/(?P<id>[^@$&+,/:;=?]+)$',
        views.OrganisationAdminGroupDetailView.as_view(),
        name='publisher-admingroup-detail'
    ),
    url(
        r'^(?P<publisher_id>[^@$&+,/:;=?]+)/group/$',
        views.OrganisationGroupView.as_view(),
        name='publisher-group-list'
    ),
    url(
        r'^(?P<publisher_id>[^@$&+,/:;=?]+)/group/(?P<id>[^@$&+,/:;=?]+)$',
        views.OrganisationGroupDetailView.as_view(),
        name='publisher-group-detail'
    ),
    url(
        r'^(?P<publisher_id>[^@$&+,/:;=?]+)/verify-api-key/$',
        views.OrganisationVerifyApiKey.as_view(),
        name='publisher-detail'
    ),
]
