
from tastypie.resources import ModelResource
from geodata.models import Country, Region, City

class OnlyCountryResource(ModelResource):
    class Meta:
        queryset = Country.objects.all().order_by('name')
        include_resource_uri = False
        excludes = ['center_longlat', 'dac_country_code', 'dac_region_code', 'dac_region_name', 'iso3', 'language', 'polygon', 'alpha3', 'fips10', 'numerical_code_un']
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
        limit = 150

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


