from django.conf.urls import include, url

from api import views

urlpatterns = [
    url(r'^$', views.welcome, name='api-root'),
    url(r'^health-check/', views.health_check, name='api-health-check'),
    url(r'^activities/', include('api.activity.urls', namespace='activities')),
    url(r'^codelists/', include('api.codelist.urls', namespace='codelists')),
    url(r'^budgets/', include('api.budget.urls', namespace='budgets')),
    url(r'^export/', include('api.export.urls', namespace='export')),
    url(r'^export_organisation/',
        include('api.export_organisation.urls',
                namespace='export_organisation')),
    url(r'^regions/', include('api.region.urls', namespace='regions')),
    url(r'^countries/', include('api.country.urls', namespace='countries')),
    url(r'^locations/', include('api.location.urls', namespace='locations')),
    url(r'^organisations/', include(
        'api.organisation.urls', namespace='organisations'
    )),
    url(r'^sectors/', include('api.sector.urls', namespace='sectors')),
    url(r'^transactions/', include(
        'api.transaction.urls', namespace='transactions'
    )),
    url(r'^results/', include('api.result.urls', namespace='results')),
    url(r'^datasets/', include('api.dataset.urls', namespace='datasets')),
    url(r'^publishers/', include(
        'api.publisher.urls', namespace='publishers'
    )),

    # This endpoint is not working yet, so we remove it just for now
    # url(r'^chains/', include('api.chain.urls', namespace='chains')),

    # TODO: no email confirmation? - 2016-10-18
    url(r'^auth/', include('rest_auth.urls')),
    url(r'^auth/registration/', include('rest_auth.registration.urls')),
    url(r'^branch/', include('api.branch.urls', namespace='branch')),
]
