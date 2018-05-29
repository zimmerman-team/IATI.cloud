from django.conf.urls import url
from django.views.decorators.cache import cache_page

from api.dataset import views
from OIPA.production_settings import API_CACHE_SECONDS

app_name = 'api'
urlpatterns = [
    url(r'^$',
        views.DatasetList.as_view(), name='dataset-list'),
    url(r'^aggregations/',
        cache_page(API_CACHE_SECONDS)(views.DatasetAggregations.as_view()),
        name='dataset-aggregations'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/$',
        views.DatasetDetail.as_view(),
        name='dataset-detail'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/notes/',
        views.DatasetNotes.as_view(),
        name='dataset-notes'),

    # TODO: temporary soln until we have implemented datasets properly -
    # 2016-10-25
    url(
        r'^(?P<publisher_id>[^@$&+,/:;=?]+)/publish_activities/$',
        views.DatasetPublishActivities.as_view(),
        name='dataset-publish'
    ),
    url(
        r'^(?P<publisher_id>[^@$&+,/:;=?]+)/publish_activities/(?P<dataset_id>[^@$&+,/:;=?]+)$',  # NOQA: E501
        views.DatasetPublishActivitiesUpdate.as_view(),
        name='dataset-publish'
    ),
    url(
        r'^(?P<publisher_id>[^@$&+,/:;=?]+)/publish_organisations/$',
        views.DatasetPublishOrganisations.as_view(),
        name='dataset-publish'
    ),
    url(
        r'^(?P<publisher_id>[^@$&+,/:;=?]+)/publish_organisations/(?P<dataset_id>[^@$&+,/:;=?]+)$',  # NOQA: E501
        views.DatasetPublishOrganisationsUpdate.as_view(),
        name='dataset-publish'
    ),
]
