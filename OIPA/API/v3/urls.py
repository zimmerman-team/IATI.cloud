# Django specific
from django.conf.urls import *
from django.http import HttpResponseRedirect
from tastypie.api import Api

from API.v3.resources.model_resources import *
from API.v3.resources.advanced_resources import *
from API.v3.resources.activity_view_resources import *

from API.v2.urls import v2_api;

v3_api = Api(api_name='v3')
v3_api.register(OrganisationResource())
v3_api.register(ActivityResource())
v3_api.register(CityResource())
v3_api.register(CountryResource())
v3_api.register(CountryGeoResource())
v3_api.register(RegionResource())
v3_api.register(SectorResource())
v3_api.register(IndicatorResource())
v3_api.register(IndicatorFiltersResource())
v3_api.register(OnlyCityResource())
v3_api.register(OnlyCountryResource())
v3_api.register(OnlyRegionResource())
v3_api.register(RecipientCountryResource())





def api_v3_docs(request):
    return HttpResponseRedirect('/api/v3/docs/')

urlpatterns = patterns('',
    url(r'^$', api_v3_docs),
    (r'^v3/$', api_v3_docs),
    url(r'^v2/docs/$', 'API.v2.views.docs_index', name='docsv2'),
    url(r'^v2/docs/getting-started/$', 'API.v2.views.docs_start', name='start_docsv2'),
    url(r'^v2/docs/resources/$', 'API.v2.views.docs_resources', name='resource_docsv2'),
    url(r'^v2/docs/filtering/$', 'API.v2.views.docs_filtering', name='filter_docsv2'),
    url(r'^v2/docs/ordering/$', 'API.v2.views.docs_ordering', name='ordering_docsv2'),
    url(r'^v2/docs/about/$', 'API.v2.views.docs_about', name='about_docsv2'),
    url(r'^v3/docs/$', 'API.v3.views.docs_index', name='docs'),
    url(r'^v3/docs/getting-started/$', 'API.v3.views.docs_start', name='start_docs'),
    url(r'^v3/docs/resources/$', 'API.v3.views.docs_resources', name='resource_docs'),
    url(r'^v3/docs/filtering/$', 'API.v3.views.docs_filtering', name='filter_docs'),
    url(r'^v3/docs/ordering/$', 'API.v3.views.docs_ordering', name='ordering_docs'),
    url(r'^v3/docs/about/$', 'API.v3.views.docs_about', name='about_docs'),
    url(r'^v3/indicator-data/$', 'API.v3.views.indicator_data_response'),
    url(r'^v3/activity-filter-options/$', 'API.v3.views.activity_filter_options'),
    url(r'^v3/indicator-filter-options/$', 'API.v3.views.indicator_filter_options'),
    url(r'^v3/country-geojson/$', 'API.v3.views.country_geojson_response'),
    (r'', include(v3_api.urls)),
    (r'', include(v2_api.urls)),
)
