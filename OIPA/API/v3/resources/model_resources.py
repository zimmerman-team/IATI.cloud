# Django specific
from django.db.models import Q

# Tastypie specific
from tastypie import fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer

# Data specific
from IATI.models import activity, organisation
from indicators.models import *
from API.v3.resources.helper_resources import *
from API.cache import NoTransformCache
from API.v3.resources.advanced_resources import *

class CityResource(ModelResource):

    class Meta:
        queryset = city.objects.all()
        resource_name = 'cities'
        include_resource_uri = False
        serializer = Serializer(formats=['xml', 'json'])

class CountryResource(ModelResource):
    capital_city = fields.OneToOneField(CityResource, 'capital_city', full=True, null=True)
    activities = fields.ToManyField(RecipientCountryResource, attribute=lambda bundle: activity_recipient_country.objects.filter(country=bundle.obj), null=True)

    class Meta:
        queryset = country.objects.all()
        resource_name = 'countries'
        excludes = ['polygon']
        include_resource_uri = False
        serializer = Serializer(formats=['xml', 'json'])

    def dehydrate(self, bundle):
        bundle.data['activities'] = bundle.obj.activity_recipient_country_set.count()
        bundle.data['region_id'] = bundle.obj.region_id
        return bundle


class CountryGeoResource(ModelResource):

    class Meta:
        queryset = country.objects.all()
        resource_name = 'country-polygons'
        excludes = ['dac_country_code', 'dac_region_code', 'dac_region_name', 'iso3', 'language']
        include_resource_uri = False
        serializer = Serializer(formats=['xml', 'json'])


class RegionResource(ModelResource):

    class Meta:
        queryset = region.objects.all()
        resource_name = 'regions'
        include_resource_uri = False
        serializer = Serializer(formats=['xml', 'json'])



class SectorResource(ModelResource):

    class Meta:
        queryset = sector.objects.all()
        resource_name = 'sectors'
        include_resource_uri = False
        serializer = Serializer(formats=['xml', 'json'])



class IndicatorResource(ModelResource):
    class Meta:
        queryset = indicator.objects.all()
        resource_name = 'indicators'
        include_resource_uri = False
        serializer = Serializer(formats=['xml', 'json'])


class IndicatorDataResource(ModelResource):


    class Meta:
        queryset = indicator_data.objects.all()
        include_resource_uri = False

class CountryIndicatorDataResource(ModelResource):
    # countries = fields.ToManyField(CountryResource, 'country_set', full=True, null=True)
    # years = fields.ToManyField(IndicatorDataResource, "indicator", full=True, null=True)
    years = fields.ToManyField(IndicatorDataResource, attribute=lambda bundle: indicator_data.objects.filter(indicator=bundle.obj), null=True)


    class Meta:
        queryset = indicator.objects.all()
        resource_name = 'indicatordata'
        include_resource_uri = False
        # TO DO: bugfix
        filtering = {
            'name': ALL
        }
        serializer = Serializer(formats=['xml', 'json'])

    # def dehydrate(self, bundle):
    #     bundle.data['country'] = bundle.obj.country.code
    #     bundle.data['indicator'] = bundle.obj.indicator.name
    #     return bundle



class OrganisationResource(ModelResource):
    type = fields.OneToOneField(OrganisationTypeResource, 'type', full=True, null=True)

    class Meta:
        queryset = organisation.objects.all()
        resource_name = 'organisations'
        serializer = Serializer(formats=['xml', 'json'])
        filtering = {
            # example to allow field specific filtering.
            'name': ALL,
            'abbreviation': ALL
        }
