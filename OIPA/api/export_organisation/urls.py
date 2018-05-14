from django.conf.urls import url

from api.export_organisation.views import OrganisationList

app_name = 'api'
urlpatterns = [
    url(r'^organisations/',
        OrganisationList.as_view(),
        name='organisation-export'),
    # url(r'^organisations/',
    #     api.organisation.views.organisationAggregations.as_view(),
    #     name='organisation-aggregations'),
]
