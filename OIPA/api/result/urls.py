from django.conf.urls import url

from api.result.views import ResultAggregations, ResultList

app_name = 'api'
urlpatterns = [
    url(r'^$', ResultList.as_view(), name='result-list'),
    url(r'^aggregations/', ResultAggregations.as_view(),
        name='result-aggregations'),
]
