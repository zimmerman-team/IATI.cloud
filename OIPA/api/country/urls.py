from django.conf.urls import url

from api.country import views

app_name = 'api'
urlpatterns = [
    url(r'^$', views.CountryList.as_view(), name='country-list'),
    url(
        r'^(?P<pk>[A-Za-z]+)/$',
        views.CountryDetail.as_view(),
        name='country-detail'
    ),
]
