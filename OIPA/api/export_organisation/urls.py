from django.conf.urls import url

from api.export_organisation.views import OrganisationList

urlpatterns = [
    url(r'^organisations/',
        OrganisationList.as_view(),
        name='organisation-export'),
    # url(r'^organisations/',
    #     api.organisation.views.organisationAggregations.as_view(),
    #     name='organisation-aggregations'),
]
