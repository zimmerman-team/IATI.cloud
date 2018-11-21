from django.conf.urls import url

from api.codelist.views import CodelistItemList, CodelistMetaList

app_name = 'api'
urlpatterns = [
    url(r'^(?P<codelist>[^@$&+,/:;=?]+)/$',
        CodelistItemList.as_view(),
        name='codelist-items-list'),
    url(r'^$',
        CodelistMetaList.as_view(), name='codelist-meta-list'),
]
