from django.conf.urls import url
from api.budget import views

urlpatterns = [
    url(r'^aggregations/', views.BudgetAggregations.as_view(),
        name='budget-aggregations'),
]
