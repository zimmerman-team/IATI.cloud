from django.conf.urls import url
from api.dataset import views


urlpatterns = [
    url(r'^$',
        views.DatasetList.as_view(), name='dataset-list'),
    url(
        r'^(?P<pk>[^@$&+,/:;=?]+)/$',
        views.DatasetDetail.as_view(),
        name='dataset-detail'),
]