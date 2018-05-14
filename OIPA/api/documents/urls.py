from django.conf.urls import url
import api.documents.views

app_name = 'api'
urlpatterns = [
    url(r'^$',
        api.documents.views.DocumentList.as_view(),
        name='document-list'),
]
