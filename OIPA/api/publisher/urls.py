from django.conf.urls import url
from api.publisher import views


urlpatterns = [
    url(r'^$', 
        views.PublisherList.as_view(), 
        name='publisher-list'
    ),
    url(
        r'^(?P<pk>[^@$&+,/:;=?]+)/$',
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
        r'^api_key/verify/$',
        views.OrganisationVerifyApiKey.as_view(),
        name='publisher-verify-api-key'
    ),
    url(
        r'^api_key/remove/$',
        views.OrganisationRemoveApiKey.as_view(),
        name='publisher-verify-api-key'
    ),
]
