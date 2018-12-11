from django.conf.urls import url

from api.branch import views

app_name = 'api'
urlpatterns = [
    url(r'^$', views.GitBranch.as_view(), name='git-branch'),
]
