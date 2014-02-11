# Django specific
from django.conf.urls import *
from django.http import HttpResponseRedirect
from tastypie.api import Api

from apip.v3.resources.model_resources import OrganisationResource, CityResource, CountryResource, RegionResource, SectorResource, RecipientCountryResource
from apip.v3.resources.advanced_resources import OnlyCityResource, OnlyRegionResource, OnlyCountryResource
from apip.v3.resources.activity_view_resources import ActivityResource
from apip.v3.resources.activity_list_resources import ActivityListResource
from apip.v3.resources.sql_resources import ActivityFilterOptionsResource, IndicatorCountryDataResource, IndicatorCityDataResource, IndicatorRegionDataResource, IndicatorRegionFilterOptionsResource, IndicatorCountryFilterOptionsResource, IndicatorCityFilterOptionsResource, CountryGeojsonResource, Adm1RegionGeojsonResource
from apip.v2 import views as old_views
from apip.v3 import views

from apip.v2.urls import v2_api;

v3_api = Api(api_name='v3')
v3_api.register(OrganisationResource())
v3_api.register(ActivityResource())
v3_api.register(ActivityListResource())
v3_api.register(ActivityFilterOptionsResource())
v3_api.register(CityResource())
v3_api.register(CountryResource())
v3_api.register(RegionResource())
v3_api.register(SectorResource())
v3_api.register(OnlyCityResource())
v3_api.register(OnlyCountryResource())
v3_api.register(OnlyRegionResource())
v3_api.register(RecipientCountryResource())
v3_api.register(IndicatorCountryDataResource())
v3_api.register(IndicatorCityDataResource())
v3_api.register(IndicatorRegionDataResource())
v3_api.register(IndicatorRegionFilterOptionsResource())
v3_api.register(IndicatorCountryFilterOptionsResource())
v3_api.register(IndicatorCityFilterOptionsResource())
v3_api.register(CountryGeojsonResource())
v3_api.register(Adm1RegionGeojsonResource())


def api_v3_docs(request):
    return HttpResponseRedirect('/apip/v3/docs/')

urlpatterns = patterns('',
    url(r'^v2/docs/$', 'apip.v2.views.docs_index', name='docsv2'),
    url(r'^v2/docs/getting-started/$', 'apip.v2.views.docs_start', name='start_docsv2'),
    url(r'^v2/docs/resources/$', old_views.docs_resources, name='resource_docsv2'),
    url(r'^v2/docs/filtering/$', old_views.docs_filtering, name='filter_docsv2'),
    url(r'^v2/docs/ordering/$', old_views.docs_ordering, name='ordering_docsv2'),
    url(r'^v2/docs/about/$', old_views.docs_about, name='about_docsv2'),
    url(r'^v3/docs/$', views.docs_index, name='docs'),
    url(r'^v3/docs/getting-started/$', views.docs_start, name='start_docs'),
    url(r'^v3/docs/resources/$', views.docs_resources, name='resource_docs'),
    url(r'^v3/docs/filtering/$', views.docs_filtering, name='filter_docs'),
    url(r'^v3/docs/ordering/$', views.docs_ordering, name='ordering_docs'),
    url(r'^v3/docs/about/$', views.docs_about, name='about_docs'),
    (r'', include(v3_api.urls)),
    (r'', include(v2_api.urls)),
    url(r'^$', api_v3_docs),
    (r'^v3/$', api_v3_docs),
)
