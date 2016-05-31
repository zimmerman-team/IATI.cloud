from django.conf.urls import url
from api.result.views import ResultAggregations
from django.views.decorators.cache import cache_page
from OIPA.production_settings import API_CACHE_SECONDS


urlpatterns = [
    url(r'^aggregations/',
        cache_page(API_CACHE_SECONDS)(ResultAggregations.as_view()),
        name='result-aggregations'),
]
