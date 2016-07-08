from django.conf.urls import url
from api.dataset import views


urlpatterns = [
    url(r'^$',
        views.DatasetList.as_view(), name='dataset-list'),
    url(r'^aggregations/',
        views.DatasetAggregations.as_view(),
        name='dataset-aggregations'),
    url(
        r'^(?P<pk>[^@$&+,/:;=?]+)/$',
        views.DatasetDetail.as_view(),
        name='dataset-detail'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/notes/',
        views.DatasetNotes.as_view(),
        name='dataset-notes'),
]