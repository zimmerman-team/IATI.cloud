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



#
# class ActivitySearchResource(ModelResource):
#     """
#     This resource is now for example purposes, when we decide to use the search platform Haystack with engine Haystack
#
#     This is resource could be requested: http://__url__api__engine/api/v2/activity-search/search/?format=json&q=mozambique
#     This resource usages the search engine Haystack, it will request Haystack. Check search engine indexing what has been added to the
#     index: iati/search_sites.py
#
#     #todo: create a denormalized resource with all necessary attributes to return faster results.
#     """
#     class Meta:
#         queryset = activity.objects.all()
#         resource_name = 'activity-search'
#         max_limit = 100
#         serializer = Serializer(formats=['json', 'xml'])
#
#     def override_urls(self):
#         return [
#             url(r"^(?P<resource_name>%s)/search%s$" % ('activity-search', trailing_slash()), self.wrap_view('get_search'), name="api_get_search"),
#             ]
#
#
#     def get_search(self, request, **kwargs):
# #        self.method_check(request, allowed=['get'])
# #        self.is_authenticated(request)
# #        self.throttle_check(request)
#
#         # Do the query.
#         sqs = SearchQuerySet().models(activity).load_all().auto_query(request.GET.get('q', ''))
#
#         paginator = Paginator(sqs, 20)

#         try:
#             page = paginator.page(int(request.GET.get('page', 1)))
#         except InvalidPage:
#             raise Http404("Sorry, no results on that page.")
#
#         objects = []
#
#         for result in page.object_list:
#             #create a result object bundle from the Activity bundle
# #            bundle = self.build_bundle(obj=result.object, request=request)
# #            bundle = self.full_dehydrate(bundle)
#             #creating a result from the stored fields from the search engine
#             fields = result.get_stored_fields()
#
#             #we can add fields on the fly, only problem is that this will hit the database, and is causing performance
#             try:
#                 fields['sector'] = result.object.sectors.all()[0].sector.name
#             except IndexError:
#                 fields['sector'] = 'N/A'
#             fields['id'] = result.object.pk
#             objects.append(fields)
#
#         object_list = {
#             'objects': objects,
#             }
#
# #        self.log_throttled_access(request)
#         return self.create_response(request, object_list)





