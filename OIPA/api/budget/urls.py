from django.conf.urls import url

from api.budget import views

app_name = 'api'
urlpatterns = [
    url(r'^$',
        views.BudgetList.as_view(),
        name='budget-list'),
    url(r'^aggregations/', views.BudgetAggregations.as_view(),
        name='budget-aggregations'),
]
