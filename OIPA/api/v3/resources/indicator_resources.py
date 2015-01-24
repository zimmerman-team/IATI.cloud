# Tastypie specific
from tastypie.resources import ModelResource

# cache specific
from api.cache import NoTransformCache
from iati.models import AidType

# Direct sql specific
import ujson
from django.db import connection
from django.http import HttpResponse

# Helpers
from api.v3.resources.custom_call_helper import CustomCallHelper


class IndicatorFilterOptionsResource(ModelResource):

    class Meta:
        #aid_type is used as dummy
        queryset = AidType.objects.all()
        resource_name = 'indicator-filter-options'
        include_resource_uri = True
        cache = NoTransformCache()
        allowed_methods = ['get']

    def get_list(self, request, **kwargs):
        helper = CustomCallHelper()
        city_q = helper.get_and_query(request, 'cities__in', 'city.id') or ""
        country_q = helper.get_and_query(request, 'countries__in', 'country.code') or ""
        region_q = helper.get_and_query(request, 'regions__in', 'region.code') or ""
        indicator_q = helper.get_and_query(request, 'indicators__in', 'i.indicator_id') or ""
        category_q = helper.get_and_query(request, 'categories__in', 'ind.category') or ""
        adm_division_q = request.GET.get("adm_division__in", "city,country,region") or ""
        adm_divisions = adm_division_q.split(",")

        filter_string = ' AND (' + city_q + country_q + region_q + indicator_q + category_q + ')'
        if 'AND ()' in filter_string:
            filter_string = filter_string[:-6]

        regions = {}
        countries = {}
        cities = {}
        indicators = {}
        jsondata = {}

        if "city" in adm_divisions:
            cursor = connection.cursor()
            # city filters
            cursor.execute('SELECT DISTINCT i.indicator_id, i.selection_type ,ind.friendly_label, ind.category as indicator_category, city.id as city_id, city.name as city_name, country.code as country_id, country.name as country_name, region.code as region_id, region.name as region_name '
                           'FROM indicator_indicatordata i '
                           'JOIN indicator_indicator ind ON i.indicator_id = ind.id '
                           'JOIN geodata_city city ON i.city_id=city.id '
                           'LEFT OUTER JOIN geodata_country country on city.country_id = country.code '
                           'LEFT OUTER JOIN geodata_region region on country.region_id = region.code '
                           'WHERE 1 %s ' % (filter_string))

            desc = cursor.description
            city_results = [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
            ]


            for r in city_results:

                region = {}
                if r['region_id']:
                    region[r['region_id']] = r['region_name']
                    regions.update(region)

                country = {}
                if r['country_id']:
                    country[r['country_id']] = r['country_name']
                    countries.update(country)

                city = {}
                if r['city_id']:
                    city[r['city_id']] = r['city_name']
                    cities.update(city)

                if r['indicator_id']:
                    if not r['indicator_id'] in indicators:
                        indicators[r['indicator_id']] = {"name": r['friendly_label'], "category": r['indicator_category'], "selection_types": []}
                    if r['selection_type'] and r['selection_type'] not in indicators[r['indicator_id']]["selection_types"]:
                        indicators[r['indicator_id']]["selection_types"].append(r['selection_type'])


        if "country" in adm_divisions:
            # country filters
            filter_string = ' AND (' + country_q + region_q + indicator_q + category_q + ')'
            if 'AND ()' in filter_string:
                filter_string = filter_string[:-6]
            cursor = connection.cursor()
            cursor.execute('SELECT DISTINCT i.indicator_id, i.selection_type, ind.friendly_label, ind.category as indicator_category, country.code as country_id, country.name as country_name, region.code as region_id, region.name as region_name '
                           'FROM indicator_indicatordata i '
                           'JOIN indicator_indicator ind ON i.indicator_id = ind.id '
                           'JOIN geodata_country country on i.country_id = country.code '
                           'LEFT OUTER JOIN geodata_region region on country.region_id = region.code '
                           'WHERE 1 %s ' % (filter_string))

            desc = cursor.description
            country_results = [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
            ]

            for r in country_results:

                region = {}
                if r['region_id']:
                    region[r['region_id']] = r['region_name']
                    regions.update(region)

                country = {}
                if r['country_id']:
                    country[r['country_id']] = r['country_name']
                    countries.update(country)

                if r['indicator_id']:
                    if not r['indicator_id'] in indicators not in indicators[r['indicator_id']]["selection_types"]:
                        indicators[r['indicator_id']] = {"name": r['friendly_label'], "category": r['indicator_category'], "selection_types": []}
                    if r['selection_type'] and r['selection_type'] not in indicators[r['indicator_id']]["selection_types"]:
                        indicators[r['indicator_id']]["selection_types"].append(r['selection_type'])


        if "region" in adm_divisions:
            # region filters
            filter_string = ' AND (' + region_q + indicator_q + category_q + ')'
            if 'AND ()' in filter_string:
                filter_string = filter_string[:-6]
            cursor = connection.cursor()
            cursor.execute('SELECT DISTINCT i.indicator_id, i.selection_type ,ind.friendly_label, ind.category as indicator_category, region.code as region_id, region.name as region_name '
                           'FROM indicator_indicatordata i '
                           'JOIN indicator_indicator ind ON i.indicator_id = ind.id '
                           'JOIN geodata_region region on i.region_id = region.code '
                           'WHERE 1 %s ' % (filter_string))

            desc = cursor.description
            region_results = [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
            ]

            for r in region_results:

                region = {}
                if r['region_id']:
                    region[r['region_id']] = r['region_name']
                    regions.update(region)

                if r['indicator_id']:
                    if not r['indicator_id'] in indicators:
                        indicators[r['indicator_id']] = {"name": r['friendly_label'], "category": r['indicator_category'], "selection_types": []}
                    if r['selection_type'] and r['selection_type'] not in indicators[r['indicator_id']]["selection_types"]:
                        indicators[r['indicator_id']]["selection_types"].append(r['selection_type'])

        jsondata['regions'] = regions
        jsondata['countries'] = countries
        jsondata['cities'] = cities
        jsondata['indicators'] = indicators

        return HttpResponse(ujson.dumps(jsondata), content_type='application/json')