from django.conf.urls import patterns, url
import api.activity.views
import api.sector.views


urlpatterns = patterns(
    '',
    url(r'^$',
        api.activity.views.ActivityList.as_view(),
        name='activity-list'),
    url(r'^/(?P<pk>[^@$&+,/:;=?]+)$',
        api.activity.views.ActivityDetail.as_view(),
        name='activity-detail'),
    url(r'^/(?P<pk>[^@$&+,/:;=?]+)/sectors$',
        api.activity.views.ActivitySectors.as_view(),
        name='activity-sectors'),
    url(r'^/(?P<pk>[^@$&+,/:;=?]+)/participating-orgs$',
        api.activity.views.ActivityParticipatingOrganisations.as_view(),
        name='activity-participating-organisations'),
    url(r'^/(?P<pk>[^@$&+,/:;=?]+)/recipient-countries$',
        api.activity.views.ActivityRecipientCountries.as_view(),
        name='activity-recipient-countries'),
    url(r'^/(?P<pk>[^@$&+,/:;=?]+)/recipient-regions',
        api.activity.views.ActivityRecipientRegions.as_view(),
        name='activity-recipient-regions'),
    url(r'^/(?P<pk>[^@$&+,/:;=?]+)/transactions',
        api.activity.views.ActivityTransactions.as_view(),
        name='activity-transactions'),
)
