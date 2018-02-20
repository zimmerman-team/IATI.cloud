from django.conf.urls import url
import api.documents.views


urlpatterns = [
    url(r'^$',
        api.documents.views.DocumentList.as_view(),
        name='document-list'),
]
