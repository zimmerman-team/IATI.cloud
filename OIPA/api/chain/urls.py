from django.conf.urls import url
import api.chain.views


urlpatterns = [
    url(r'^$',
        api.chain.views.ChainList.as_view(),
        name='chain-list'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/links/',
        api.chain.views.ChainLinkList.as_view(),
        name='chain-link-list'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/errors/',
        api.chain.views.ChainNodeErrorList.as_view(),
        name='chain-error-list'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/activities/',
        api.chain.views.ChainActivities.as_view(),
        name='chain-activity-list'),
    url(r'^(?P<pk>[^@$&+,/:;=?]+)/',
        api.chain.views.ChainDetail.as_view(),
        name='chain-detail'),
    ]
