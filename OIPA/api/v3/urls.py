# Django specific
from django.conf.urls import *
from django.http import HttpResponseRedirect
from tastypie.api import Api

from api.v3.resources.model_resources import OrganisationResource, CityResource, CountryResource, RegionResource, SectorResource, RecipientCountryResource
from api.v3.resources.advanced_resources import OnlyCityResource, OnlyRegionResource, OnlyCountryResource
from api.v3.resources.activity_view_resources import ActivityResource
from api.v3.resources.activity_list_resources import ActivityListResource
from api.v3.resources.sql_resources import ActivityListVisResource, ActivityFilterOptionsResource, CountryGeojsonResource, Adm1RegionGeojsonResource, CountryActivitiesResource, RegionActivitiesResource, GlobalActivitiesResource,  DonorActivitiesResource, SectorActivitiesResource, ActivityFilterOptionsUnescoResource
from api.v3.resources.aggregation_resources import ActivityCountResource, ActivityAggregatedAnyResource, ActivityAggregatedAnyNamesResource
from api.v3.resources.indicator_resources import IndicatorAggregationResource, IndicatorCountryDataResource, IndicatorCityDataResource, IndicatorRegionDataResource, IndicatorFilterOptionsResource, IndicatorDataResource
from api.v2 import views as old_views
from api.v3 import views

from api.v2.urls import v2_api
from api.v3.resources.unesco_indicator_resources import UnescoIndicatorResource

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
v3_api.register(CountryGeojsonResource())
v3_api.register(Adm1RegionGeojsonResource())
v3_api.register(CountryActivitiesResource())
v3_api.register(ActivityCountResource())
v3_api.register(ActivityAggregatedAnyResource())
v3_api.register(IndicatorAggregationResource())
v3_api.register(ActivityAggregatedAnyNamesResource())
v3_api.register(IndicatorFilterOptionsResource())
v3_api.register(IndicatorDataResource())
v3_api.register(RegionActivitiesResource())
v3_api.register(GlobalActivitiesResource())
v3_api.register(DonorActivitiesResource())
v3_api.register(SectorActivitiesResource())
v3_api.register(UnescoIndicatorResource())
v3_api.register(ActivityFilterOptionsUnescoResource())
v3_api.register(ActivityListVisResource())



def api_v3_docs(request):
    return HttpResponseRedirect('/api/v3/docs/')

urlpatterns = patterns('',
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
