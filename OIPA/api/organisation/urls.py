from django.conf.urls import patterns, url
from api.organisation import views


urlpatterns = patterns(
    '',
    url(r'^$', views.OrganisationList.as_view(), name='organisation-list'),
    url(
        r'^(?P<pk>[^@$&+,/:;=?]+)/$',
        views.OrganisationDetail.as_view(),
        name='organisation-detail'
    ),
)
