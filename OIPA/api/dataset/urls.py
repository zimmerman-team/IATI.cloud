from django.conf.urls import url
from api.dataset import views
from django.views.decorators.cache import cache_page
from OIPA.production_settings import API_CACHE_SECONDS

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

    # TODO: temporary soln until we have implemented datasets properly - 2016-10-25
    url(
        r'^(?P<publisher_id>[^@$&+,/:;=?]+)/publish_activities/$',
        views.DatasetPublishActivities.as_view(),
        name='dataset-publish'
    ),
]
