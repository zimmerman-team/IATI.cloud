
from tastypie.resources import ModelResource
from geodata.models import Country, Region, City
from indicator.models import Indicator
from tastypie import fields
from tastypie.serializers import Serializer



class IndicatorFiltersResource(ModelResource):
    name = fields.CharField(attribute='name')


    class Meta:
        queryset = Indicator.objects.all()
        resource_name = 'indicator-filters'
        serializer = Serializer(formats=['xml', 'json'])
        excludes = ['description', 'type_data', 'selection_type', 'deprivation_type', 'rain_programme']
        include_resource_uri = False
    # def dehydrate(self, bundle):
    #     bundle.data['region_id'] = bundle.obj.country.region_id
    #
    #
    def dehydrate_name(selfself, bundle):
        return bundle.data['name']


class OnlyCountryResource(ModelResource):
    class Meta:
        queryset = Country.objects.all().order_by('name')
        include_resource_uri = False
        excludes = ['center_longlat', 'dac_country_code', 'dac_region_code', 'dac_region_name', 'iso3', 'language', 'polygon']
        resource_name = 'country'
        limit = 1000


class OnlyRegionResource(ModelResource):
    class Meta:
        queryset = Region.objects.all().distinct().order_by('code')
        resource_name = 'region'
        include_resource_uri = False

class OnlyCityResource(ModelResource):
    class Meta:
        queryset = City.objects.all().order_by('name')
        resource_name = 'city'
        include_resource_uri = False
        excludes = ['alt_name', 'ascii_name', 'geoname_id', 'location']

    def dehydrate(self, bundle):
        bundle.data['country'] = bundle.obj.country.code
        return bundle

    def apply_filters(self, request, applicable_filters):
        base_object_list = super(OnlyCityResource, self).apply_filters(request, applicable_filters)
        countries = request.GET.get('country', None)

        filters = {}
        if countries:
            countries = countries.replace('|', ',').replace('-', ',').split(',')
            filters.update(dict(country__iso__in=countries))

        return base_object_list.filter(**filters).distinct()












#
# class UnHabitatIndicatorCountryResource(ModelResource):
#     class Meta:
#         queryset = UnHabitatIndicatorCountry.objects.all()
#         include_resource_uri = False
#         resource_name = 'indicator-country'
#         serializer = Serializer(formats=['xml', 'json'])
#         filtering = {"year": ALL }
# #        authentication = ApiKeyAuthentication()
#
#
#     def dehydrate(self, bundle):
#         bundle.data['country_iso'] = bundle.obj.country.iso
#         bundle.data['country_iso3'] = bundle.obj.country.iso3
#
#         bundle.data['country_name'] = bundle.obj.country.get_iso_display()
#         bundle.data['dac_region_code'] = bundle.obj.country.dac_region_code
#         bundle.data['dac_region_name'] = bundle.obj.country.dac_region_name
#         tpset = bundle.obj.typedeprivationcountry_set.all()
#         tp_list = {}
#         for tp in tpset:
#             temp_list = {}
#             temp_list['type'] = tp.get_type_deprivation_display()
#             temp_list['non_slum_household'] = tp.non_slum_household
#             temp_list['slum_household'] = tp.slum_household
#             temp_list['one_shelter_deprivation'] = tp.one_shelter_deprivation
#             temp_list['two_shelter_deprivations'] = tp.two_shelter_deprivations
#             temp_list['three_shelter_deprivations'] = tp.three_shelter_deprivations
#             temp_list['four_shelter_deprivations'] = tp.four_shelter_deprivations
#             temp_list['gender'] = tp.gender
#             temp_list['extra_type_name'] = tp.extra_type_name
#             temp_list['is_matrix'] = tp.is_matrix
#             temp_list['urban'] = tp.urban
#             temp_list['total'] = tp.total
#             temp_list['rural'] = tp.rural
#
#             tp_list['deprivation_id_'+str(tp.id)] = temp_list
#         bundle.data['deprivation'] = tp_list
#         bundle.data.pop('id')
#
#         return bundle
#
#     def apply_filters(self, request, applicable_filters):
#         base_object_list = super(UnHabitatIndicatorCountryResource, self).apply_filters(request, applicable_filters)
#         regions = request.GET.get('regions', None)
#         countries = request.GET.get('country_name', None)
#         isos = request.GET.get('iso', None)
#         indicator = request.GET.get('indicator', None)
#
#
#
#         filters = {}
#         if regions:
#             # @todo: implement smart filtering with seperator detection
#             regions = regions.replace('|', ',').replace('-', ',').split(',')
#             filters.update(dict(country__dac_region_code__in=regions))
#         if countries:
#             countries = countries.replace('|', ',').replace('-', ',').split(',')
#             filters.update(dict(country__country_name__in=countries))
#         if isos:
#             isos = isos.replace('|', ',').replace('-', ',').split(',')
#             filters.update(dict(country__iso__in=isos))
# #
#
#         return base_object_list.filter(**filters).distinct()
#

#
# class UnHabitatIndicatorcityResource(ModelResource):
#     class Meta:
#         queryset = UnHabitatIndicatorcity.objects.all()
#         include_resource_uri = False
#         resource_name = 'indicator-city'
#         serializer = Serializer(formats=['xml', 'json'])
#         filtering = {"year": ALL }
#     #        authentication = ApiKeyAuthentication()
#
#
#     def dehydrate(self, bundle):
#         bundle.data['country_iso'] = bundle.obj.city.country.iso
#         bundle.data['country_name'] = bundle.obj.city.country.get_iso_display()
#         bundle.data['dac_region_code'] = bundle.obj.city.country.dac_region_code
#         bundle.data['dac_region_name'] = bundle.obj.city.country.dac_region_name
#         bundle.data['city_name'] = bundle.obj.city.name
#
#     #        bundle.data['']
#
#         bundle.data.pop('id')
#
#         return bundle
#
#     def apply_filters(self, request, applicable_filters):
#         base_object_list = super(UnHabitatIndicatorcityResource, self).apply_filters(request, applicable_filters)
#         regions = request.GET.get('regions', None)
#         countries = request.GET.get('country_name', None)
#         isos = request.GET.get('iso', None)
#         city = request.GET.get('city', None)
#
#
#
#         filters = {}
#         if regions:
#             # @todo: implement smart filtering with seperator detection
#             regions = regions.replace('|', ',').replace('-', ',').split(',')
#             filters.update(dict(city__country__dac_region_code__in=regions))
#         if countries:
#             countries = countries.replace('|', ',').replace('-', ',').split(',')
#             filters.update(dict(city__country__country_name__in=countries))
#         if isos:
#             isos = isos.replace('|', ',').replace('-', ',').split(',')
#             filters.update(dict(city__country__iso__in=isos))
#         if city:
#             city = city.replace('|', ',').replace('-', ',').split(',')
#
#             filters.update(dict(city__name__in=city))
#
#         return base_object_list.filter(**filters).distinct()
#
#
#
