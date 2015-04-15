from django.conf.urls import *
from django.http import HttpResponseRedirect
from tastypie.api import Api
from api.v3.resources.model_resources import OrganisationResource
from api.v3.resources.model_resources import CityResource
from api.v3.resources.model_resources import CountryResource
from api.v3.resources.model_resources import RegionResource
from api.v3.resources.model_resources import SectorResource
from api.v3.resources.model_resources import RecipientCountryResource
from api.v3.resources.advanced_resources import OnlyCityResource
from api.v3.resources.advanced_resources import OnlyRegionResource
from api.v3.resources.advanced_resources import OnlyCountryResource
from api.v3.resources.activity_view_resources import ActivityResource
from api.v3.resources.activity_list_resources import ActivityListResource
from api.v3.resources.sql_resources import ActivityListVisResource
from api.v3.resources.sql_resources import ActivityFilterOptionsResource
from api.v3.resources.sql_resources import CountryGeojsonResource
from api.v3.resources.sql_resources import CountryActivitiesResource
from api.v3.resources.sql_resources import RegionActivitiesResource
from api.v3.resources.sql_resources import GlobalActivitiesResource
from api.v3.resources.sql_resources import DonorActivitiesResource
from api.v3.resources.sql_resources import SectorActivitiesResource
from api.v3.resources.sql_resources import ActivityFilterOptionsUnescoResource
from api.v3.resources.sql_resources import PoliciyMarkerSectorResource
from api.v3.resources.aggregation_resources import ActivityAggregatedAnyResource
from api.v3.resources.indicator_resources import IndicatorFilterOptionsResource
from api.v3.resources.indicator_data_resource import IndicatorDataResource
from api.v3.resources.unesco_indicator_resources import UnescoIndicatorResource
from api.v3 import views

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
v3_api.register(CountryGeojsonResource())
v3_api.register(CountryActivitiesResource())
v3_api.register(ActivityAggregatedAnyResource())
v3_api.register(IndicatorFilterOptionsResource())
v3_api.register(IndicatorDataResource())
v3_api.register(RegionActivitiesResource())
v3_api.register(GlobalActivitiesResource())
v3_api.register(DonorActivitiesResource())
v3_api.register(SectorActivitiesResource())
v3_api.register(UnescoIndicatorResource())
v3_api.register(ActivityFilterOptionsUnescoResource())
v3_api.register(ActivityListVisResource())
v3_api.register(PoliciyMarkerSectorResource())

def api_v3_docs(request):
    return HttpResponseRedirect('/api/v3/docs/')

urlpatterns = patterns(
    '',
    url(r'^/docs/$', views.docs_index, name='docs'),
    url(r'^/docs/getting-started/$', views.docs_start, name='start_docs'),
    url(r'^/docs/resources/$', views.docs_resources, name='resource_docs'),
    url(r'^/docs/filtering/$', views.docs_filtering, name='filter_docs'),
    url(r'^/docs/ordering/$', views.docs_ordering, name='ordering_docs'),
    url(r'^/docs/about/$', views.docs_about, name='about_docs'),
)
