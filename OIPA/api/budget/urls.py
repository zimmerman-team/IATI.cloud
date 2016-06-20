from django.conf.urls import url
from api.budget import views
from django.views.decorators.cache import cache_page
from OIPA.production_settings import API_CACHE_SECONDS


urlpatterns = [
    url(r'^aggregations/',
        cache_page(API_CACHE_SECONDS)(views.BudgetAggregations.as_view()),
        name='budget-aggregations'),
]
