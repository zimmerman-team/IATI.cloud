# Django specific
from django.conf.urls import *
from django.http import HttpResponseRedirect
from tastypie.api import Api

# App specific
from apip.v2.resources.model_resources import *
# from apip.v2.resources.model_resources import ActivitySearchResource
from apip.v2.resources.activity_view_resources import ActivityResource
from apip.v2.resources.advanced_resources import OnlyCityResource, OnlyRegionResource, OnlyCountryResource

v2_api = Api(api_name='v2')
v2_api.register(OrganisationResource())
v2_api.register(ActivityResource())
v2_api.register(CountryResource())
v2_api.register(RegionResource())
v2_api.register(SectorResource())
v2_api.register(IndicatorResource())
v2_api.register(IndicatorDataResource())
v2_api.register(ActivityListResource())
# v2_api.register(ActivitySearchResource())
v2_api.register(OnlyCountryResource())
v2_api.register(OnlyRegionResource())
v2_api.register(OnlyCityResource())


def api_v2_docs(request):
    return HttpResponseRedirect('/apip/v2/docs/')

urlpatterns = patterns('',
    (r'^v2/', api_v2_docs),
    url(r'^v2/docs/$', 'apip.v2.views.docs_index', name='docs'),
    url(r'^v2/docs/getting-started/$', 'apip.v2.views.docs_start', name='start_docs'),
    url(r'^v2/docs/resources/$', 'apip.v2.views.docs_resources', name='resource_docs'),
    url(r'^v2/docs/filtering/$', 'apip.v2.views.docs_filtering', name='filter_docs'),
    url(r'^v2/docs/ordering/$', 'apip.v2.views.docs_ordering', name='ordering_docs'),
    url(r'^v2/docs/about/$', 'apip.v2.views.docs_about', name='about_docs'),
    (r'', include(v2_api.urls)),
)