from tastypie.serializers import Serializer
from indicator.models import *
from api.v3.resources.helper_resources import *



class RegionResource(ModelResource):

    class Meta:
        queryset = Region.objects.all()
        resource_name = 'regions'
        include_resource_uri = False
        serializer = Serializer(formats=['xml', 'json'])
        allowed_methods = ['get']

class CityResource(ModelResource):

    class Meta:
        queryset = City.objects.all()
        resource_name = 'cities'
        include_resource_uri = False
        serializer = Serializer(formats=['xml', 'json'])
        filtering = {
            'id': ['exact'],
        }
        allowed_methods = ['get']

    def dehydrate(self, bundle):
        bundle.data['country_id'] = bundle.obj.country_id
        return bundle


class CountryResource(ModelResource):
    capital_city = fields.OneToOneField(CityResource, 'capital_city', full=True, null=True)
    unesco_region = fields.ForeignKey(RegionResource, 'unesco_region', full=True, null=True)
    cities = fields.ToManyField(CityResource, 'city_set', full=True, null=True, use_in="detail")


    class Meta:
        queryset = Country.objects.all()
        resource_name = 'countries'
        # excludes = ['polygon']
        include_resource_uri = False
        serializer = Serializer(formats=['xml', 'json'])
        filtering = {
            'code': ['exact'],
        }
        allowed_methods = ['get']

    def dehydrate(self, bundle):
        bundle.data['region_id'] = bundle.obj.region_id
        return bundle




class SectorResource(ModelResource):

    class Meta:
        queryset = Sector.objects.all()
        resource_name = 'sectors'
        include_resource_uri = False
        serializer = Serializer(formats=['xml', 'json'])
        allowed_methods = ['get']

class OrganisationResource(ModelResource):
    type = fields.OneToOneField(OrganisationTypeResource, 'type', full=True, null=True)

    class Meta:
        queryset = Organisation.objects.all()
        resource_name = 'organisations'
        serializer = Serializer(formats=['xml', 'json'])
        filtering = {
            # example to allow field specific filtering.
            'name': ALL,
            'abbreviation': ALL
        }
