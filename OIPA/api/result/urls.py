from django.conf.urls import url
from api.result.views import ResultAggregations

urlpatterns = [
    url(r'^aggregations/', ResultAggregations.as_view(),
        name='result-aggregations'),
]
