# Django specific
from django.db.models import Q

# Tastypie specific
from tastypie import fields
from tastypie.constants import ALL
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer

# Data specific
from iati.models import Activity, Organisation
from indicator.models import *
from api.v2.resources.helper_resources import *

class CityResource(ModelResource):

    class Meta:
        queryset = City.objects.all()
        resource_name = 'cities'
        include_resource_uri = False
        serializer = Serializer(formats=['xml', 'json'])

class CountryResource(ModelResource):
    # capital_city = fields.OneToOneField(CityResource, 'capital_city', full=True, null=True)
    country_name = fields.CharField('name', null=True)
    iso = fields.CharField('code', null=True)
    iso2 = fields.CharField('code', null=True)
    # activities = fields.ToManyField(RecipientCountryResource, attribute=lambda bundle: activity_recipient_country.objects.filter(country=bundle.obj), null=True)

    class Meta:
        queryset = Country.objects.all()
        resource_name = 'countries'
        excludes = ['polygon', 'code']
        include_resource_uri = False
        serializer = Serializer(formats=['xml', 'json'])

    def dehydrate(self, bundle):
        bundle.data['activities'] = bundle.obj.activity_recipient_country_set.count()
        return bundle


class CountryGeoResource(ModelResource):

    class Meta:
        queryset = Country.objects.all()
        resource_name = 'country-polygons'
        excludes = ['dac_country_code', 'dac_region_code', 'dac_region_name', 'iso3', 'language']
        include_resource_uri = False
        serializer = Serializer(formats=['xml', 'json'])


class RegionResource(ModelResource):

    class Meta:
        queryset = Region.objects.all()
        resource_name = 'regions'
        serializer = Serializer(formats=['xml', 'json'])



class SectorResource(ModelResource):

    class Meta:
        queryset = Sector.objects.all()
        resource_name = 'sectors'
        serializer = Serializer(formats=['xml', 'json'])



class IndicatorResource(ModelResource):
    class Meta:
        queryset = Indicator.objects.all()
        resource_name = 'indicator'
        include_resource_uri = False
        serializer = Serializer(formats=['xml', 'json'])


class IndicatorDataResource(ModelResource):

    class Meta:
        queryset = IndicatorData.objects.all()
        excludes = ['country.language', 'language']
        resource_name = 'indicatordata'
        include_resource_uri = False
        # TO DO: bugfix
        filtering = {
            'indicator_id': ALL
        }
        serializer = Serializer(formats=['xml', 'json'])

    def dehydrate(self, bundle):
        bundle.data['country'] = bundle.obj.country.code
        bundle.data['indicator'] = bundle.obj.indicator.name
        return bundle



class OrganisationResource(ModelResource):
    type = fields.OneToOneField(OrganisationTypeResource, 'type', full=True, null=True)
    org_name = fields.CharField('name', null=True)

    class Meta:
        queryset = Organisation.objects.all()
        resource_name = 'organisations'
        serializer = Serializer(formats=['xml', 'json'])
        filtering = {
            # example to allow field specific filtering.
            'name': ALL,
            'abbreviation': ALL
        }





class ActivityListResource(ModelResource):
    """
    Resource copied from ActivityResource with less attributes to increase result speed
    """

    recipient_country = fields.ToManyField(RecipientCountryResource, 'iatiactivitycountry_set', full=True, null=True)
    # unhabitat_indicators = fields.ToManyField(UnHabitatIndicatorCountryResource, attribute=lambda bundle: UnHabitatIndicatorCountry.objects.filter(country__pk__in=ActivityListResource.get_country(bundle)).order_by('country', 'year',), full=True, null=True)

    activity_sectors = fields.ToManyField(SectorResource, 'sectors', full=True, null=True)
    titles = fields.ToManyField(TitleResource, 'iatiactivitytitle_set', full=True, null=True)
    descriptions = fields.ToManyField(DescriptionResource, 'iatiactivitydescription_set', full=True, null=True)
    recipient_region = fields.ToManyField(RecipientRegionResource, 'iatiactivityregion_set', full=True, null=True)
    activity_sectors = fields.ToManyField(SectorResource, 'sectors', full=True, null=True)

    @staticmethod
    def get_country(bundle):
        try:
            country = bundle.obj.iatiactivitycountry_set.values('country__pk').all()
            return country
        except:
            return None


    class Meta:
        queryset = Activity.objects.all()
        resource_name = 'activity-list'
        max_limit = 100
        serializer = Serializer(formats=['xml', 'json'])

    def apply_filters(self, request, applicable_filters):
        base_object_list = super(ActivityListResource, self).apply_filters(request, applicable_filters)
        query = request.GET.get('query', None)
        sectors = request.GET.get('sectors', None)
        regions = request.GET.get('regions', None)
        countries = request.GET.get('countries', None)
        organisations = request.GET.get('organisations', None)

#        organisations = request.GET.get('organisations', None)
        filters = {}
        if sectors:
            # @todo: implement smart filtering with seperator detection
            sectors = sectors.replace('|', ',').replace('-', ',').split(',')
            filters.update(dict(sectors__sector__code__in=sectors))
        if regions:
            # @todo: implement smart filtering with seperator detection
            regions = regions.replace('|', ',').replace('-', ',').split(',')
            filters.update(dict(iatiactivityregion__region__code__in=regions))
        if countries:
            # @todo: implement smart filtering with seperator detection
            countries = countries.replace('|', ',').replace('-', ',').split(',')
            filters.update(dict(iatiactivitycountry__country__iso__in=countries))
        if organisations:
            organisations = organisations.replace('|', ',').replace('-', ',').split(',')
            filters.update(dict(reporting_organisation__ref__in=organisations))
        if query:
            query_words = query.split(' ')
            query_countries = []
            # for query_word in query_words:
            #     if query_word in COUNTRY_ISO_MAP.values() and not countries:
            #         query_countries.append([item[0] for item in COUNTRY_ISO_MAP.items() if item[1] == query_word].pop())
            if query_countries:
                qset = (
                    Q(iatiactivitycountry__country__iso__in=query_countries, **filters) |
                    Q(iatiactivitytitle__title__icontains=query, **filters) |
                    Q(iatiactivitydescription__description__icontains=query, **filters)
                    )
            else:
                qset = (
                    Q(iatiactivitytitle__title__icontains=query, **filters) |
                    Q(iatiactivitydescription__description__icontains=query, **filters)
                    )
            return base_object_list.filter(qset).distinct()
        return base_object_list.filter(**filters).distinct()
