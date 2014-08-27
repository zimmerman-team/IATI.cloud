# Django specific
from django.conf.urls import *
from tastypie.api import Api

from api.dev.resources.model_resources import OrganisationResource, CityResource, CountryResource, RegionResource, SectorResource, RecipientCountryResource
from api.dev.resources.advanced_resources import OnlyCityResource, OnlyRegionResource, OnlyCountryResource
from api.dev.resources.activity_view_resources import ActivityResource
from api.dev.resources.activity_list_resources import ActivityListResource
from api.dev.resources.sql_resources import ActivityFilterOptionsResource, CountryGeojsonResource, Adm1RegionGeojsonResource, CountryActivitiesResource, RegionActivitiesResource, GlobalActivitiesResource,  DonorActivitiesResource, SectorActivitiesResource, ActivityFilterOptionsUnescoResource
from api.dev.resources.aggregation_resources import ActivityCountResource, ActivityAggregatedAnyResource, ActivityAggregatedAnyNamesResource
from api.dev.resources.indicator_resources import IndicatorAggregationResource, IndicatorCountryDataResource, IndicatorCityDataResource, IndicatorRegionDataResource, IndicatorFilterOptionsResource, IndicatorDataResource
from api.dev.resources.unesco_indicator_resources import UnescoIndicatorResource

dev_api = Api(api_name='dev')
dev_api.register(OrganisationResource())
dev_api.register(ActivityResource())
dev_api.register(ActivityListResource())
dev_api.register(ActivityFilterOptionsResource())
dev_api.register(CityResource())
dev_api.register(CountryResource())
dev_api.register(RegionResource())
dev_api.register(SectorResource())
dev_api.register(OnlyCityResource())
dev_api.register(OnlyCountryResource())
dev_api.register(OnlyRegionResource())
dev_api.register(RecipientCountryResource())
dev_api.register(IndicatorCountryDataResource())
dev_api.register(IndicatorCityDataResource())
dev_api.register(IndicatorRegionDataResource())
dev_api.register(CountryGeojsonResource())
dev_api.register(Adm1RegionGeojsonResource())
dev_api.register(CountryActivitiesResource())
dev_api.register(ActivityCountResource())
dev_api.register(ActivityAggregatedAnyResource())
dev_api.register(IndicatorAggregationResource())
dev_api.register(ActivityAggregatedAnyNamesResource())
dev_api.register(IndicatorFilterOptionsResource())
dev_api.register(IndicatorDataResource())
dev_api.register(RegionActivitiesResource())
dev_api.register(GlobalActivitiesResource())
dev_api.register(DonorActivitiesResource())
dev_api.register(SectorActivitiesResource())
dev_api.register(UnescoIndicatorResource())
dev_api.register(ActivityFilterOptionsUnescoResource())

urlpatterns = patterns('',
    (r'', include(dev_api.urls)),
)
