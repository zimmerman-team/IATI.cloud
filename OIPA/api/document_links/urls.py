from django.conf.urls import url
import api.document_links.views


urlpatterns = [
    url(r'^$',
        api.document_links.views.DocumentList.as_view(),
        name='document-link-list'),
    ]
