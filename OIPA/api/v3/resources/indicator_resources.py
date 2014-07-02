# Tastypie specific
from tastypie.resources import ModelResource

# cache specific
from api.cache import NoTransformCache
from iati.models import AidType
from cache.validator import Validator

# Direct sql specific
import ujson
from django.db import connection
from django.http import HttpResponse

# Helpers
from api.v3.resources.custom_call_helper import CustomCallHelper

class IndicatorAggregationResource(ModelResource):

    class Meta:
        #aid_type is used as dummy
        queryset = AidType.objects.all()
        resource_name = 'indicator-region-aggregation'
        include_resource_uri = True
        cache = NoTransformCache()


    def get_list(self, request, **kwargs):

        helper = CustomCallHelper()
        cursor = connection.cursor()

        # get filters
        indicator_id = request.GET.get('indicator_id', None)

        # get indicator type
        from indicator.models import Indicator
        current_indicator = Indicator.objects.get(id=indicator_id)


        if (current_indicator.type_data == "p"):
            aggregation_type = "AVG"
        else :
            return HttpResponse(ujson.dumps(["Indicator type not recognized"]), mimetype='application/json')

        #create the query
        query = 'SELECT year, r.code as region_id, ' + aggregation_type + '(id.value) as aggregation ' \
                'FROM indicator_indicatordata as id ' \
                'JOIN geodata_country as c on id.country_id = c.code ' \
                'JOIN geodata_region as r on c.region_id = r.code ' \
                'WHERE id.indicator_id = "'+indicator_id+'" ' \
                'GROUP BY year, r.code'

        print query

        # execute query
        cursor.execute(query)
        results1 = helper.get_fields(cursor=cursor)

        # query result -> json output

        options = {}

        for r in results1:

            options[r['region_id']] = r['aggregation']

        return HttpResponse(ujson.dumps(options), mimetype='application/json')




class IndicatorCountryDataResource(ModelResource):

    class Meta:
        #aid_type is used as dummy
        queryset = AidType.objects.all()
        resource_name = 'indicator-country-data'
        include_resource_uri = True
        cache = NoTransformCache()


    def get_list(self, request, **kwargs):

        helper = CustomCallHelper()

        country_q = helper.get_and_query(request, 'countries__in', 'c.code')
        region_q = helper.get_and_query(request, 'regions__in', 'dac_region_code')
        year_q = helper.get_and_query(request, 'years__in', 'id.year')
        indicator_q = helper.get_and_query(request, 'indicators__in', 'indicator_id')

        if not indicator_q:
            return HttpResponse(ujson.dumps("No indicator given"), mimetype='application/json')

        filter_string = '  (' + country_q + region_q + year_q + indicator_q + ')'

        if 'AND ()' in filter_string:
            filter_string = filter_string[:-6]

        cursor = connection.cursor()

        cursor.execute('SELECT da.id as indicator_id, da.friendly_label, da.type_data, c.name as country_name, '
                       'id.value, id.year, AsText(c.center_longlat) as loc, c.code as country_id '
                       'FROM indicator_indicatordata id '
                       'LEFT OUTER JOIN geodata_country c ON id.country_id = c.code '
                       'LEFT OUTER JOIN indicator_indicator da ON da.id = id.indicator_id '
                       'WHERE '
                       'id.city_id is NULL '
                       'AND %s' % (filter_string))
        cursor_max = connection.cursor()

        indicator_q = indicator_q.replace(" ) AND (", "")
        cursor_max.execute('SELECT max(value) as max_value FROM indicator_indicatordata WHERE %s' % indicator_q)
        result_max = cursor_max.fetchone()
        desc = cursor.description
        results = [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
        ]
        country = {}
        for r in results:

            try:
                country[r['country_id']]['years']
            except:
                loc = r['loc']
                if loc:

                    loc = loc.replace("POINT(", "")
                    loc = loc.replace(")", "")
                    loc_array = loc.split(" ")
                    longitude = loc_array[0]
                    latitude = loc_array[1]
                else:
                    longitude = None
                    latitude = None

                country[r['country_id']] = {'name' : r['country_name'], 'country_id' : r['country_id'], 'longitude' : longitude, 'latitude' : latitude, 'indicator_friendly' : r['friendly_label'], 'type_data' : r['type_data'] , 'indicator' : r['indicator_id'],  'years' : {}}

            year = {}
            year['y' + str(r['year'])] = r['value']
            country[r['country_id']]['years'].update(year)

        country['max_value'] = result_max[0]

        return HttpResponse(ujson.dumps(country), mimetype='application/json')


class IndicatorCityDataResource(ModelResource):

    class Meta:
        #aid_type is used as dummy
        queryset = AidType.objects.all()
        resource_name = 'indicator-city-data'
        include_resource_uri = True
        cache = NoTransformCache()


    def get_list(self, request, **kwargs):
        helper = CustomCallHelper()
        city_q = helper.get_and_query(request, 'cities__in', 'city_id')
        country_q = helper.get_and_query(request, 'countries__in', 'c.code')
        region_q = helper.get_and_query(request, 'regions__in', 'r.code')
        year_q = helper.get_and_query(request, 'years__in', 'id.year')
        indicator_q = helper.get_and_query(request, 'indicators__in', 'indicator_id')

        if not indicator_q:
            return HttpResponse(ujson.dumps("No indicator given"), mimetype='application/json')

        filter_string = '  (' + city_q + country_q + region_q + year_q + indicator_q + ')'

        if 'AND ()' in filter_string:
            filter_string = filter_string[:-6]

        cursor = connection.cursor()

        cursor.execute('SELECT da.id as indicator_id, da.friendly_label, da.type_data, ci.name as city_name, '
                       'c.name as country_name, id.value, id.year, AsText(ci.location) as loc, ci.id as city_id '
                       'FROM indicator_indicatordata id '
                       'LEFT OUTER JOIN geodata_city ci ON id.city_id = ci.id '
                       'LEFT OUTER JOIN geodata_country c ON ci.country_id = c.code '
                       'LEFT OUTER JOIN geodata_region r ON c.region_id = r.code '
                       'LEFT OUTER JOIN indicator_indicator da ON da.id = id.indicator_id '
                       'WHERE '
                       'id.city_id is not NULL '
                       'AND %s' % (filter_string))

        cursor_max = connection.cursor()
        indicator_q = indicator_q.replace(" ) AND (", "")
        cursor_max.execute('SELECT max(value) as max_value FROM indicator_indicatordata WHERE %s' % indicator_q)
        result_max = cursor_max.fetchone()
        desc = cursor.description
        results = [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
        ]
        city = {}
        for r in results:

            try:
                city[r['city_id']]['years']
            except:
                loc = r['loc']
                if loc:

                    loc = loc.replace("POINT(", "")
                    loc = loc.replace(")", "")
                    loc_array = loc.split(" ")
                    longitude = loc_array[0]
                    latitude = loc_array[1]
                else:
                    longitude = None
                    latitude = None

                city[r['city_id']] = {'name' : r['city_name'], 'city_id' : r['city_id'], 'country_name' : r['country_name'], 'longitude' : longitude, 'latitude' : latitude, 'indicator_friendly' : r['friendly_label'], 'type_data' : r['type_data'] , 'indicator' : r['indicator_id'],  'years' : {}}

            year = {}
            year['y' + str(r['year'])] = r['value']
            city[r['city_id']]['years'].update(year)

        city['max_value'] = result_max[0]



        return HttpResponse(ujson.dumps(city), mimetype='application/json')




class IndicatorRegionDataResource(ModelResource):

    class Meta:
        #aid_type is used as dummy
        queryset = AidType.objects.all()
        resource_name = 'indicator-region-data'
        include_resource_uri = True
        cache = NoTransformCache()


    def get_list(self, request, **kwargs):
        helper = CustomCallHelper()
        country_q = helper.get_and_query(request, 'cities__in', 'c.code')
        region_q = helper.get_and_query(request, 'regions__in', 'dac_region_code')
        year_q = helper.get_and_query(request, 'years__in', 'id.year')
        indicator_q = helper.get_and_query(request, 'indicators__in', 'indicator_id')

        if not indicator_q:
            indicator_q = ' indicator_id = "population"'

        filter_string = '  (' + country_q + region_q + year_q + indicator_q + ')'

        if 'AND ()' in filter_string:
            filter_string = filter_string[:-6]

        cursor = connection.cursor()

        cursor.execute('SELECT da.id as indicator_id, da.friendly_label, da.type_data, c.name as country_name, c.dac_region_code, '
                       'c.dac_region_name, id.value, id.year, AsText(c.center_longlat) as loc, c.code as country_id '
                       'FROM indicator_indicatordata id '
                       'LEFT OUTER JOIN geodata_city c ON id.country_id = c.code '
                       'LEFT OUTER JOIN indicator_indicator da ON da.id = id.indicator_id WHERE %s' % (filter_string))
        cursor_max = connection.cursor()

        indicator_q = indicator_q.replace(" ) AND (", "")
        cursor_max.execute('SELECT max(value) as max_value FROM indicator_indicatordata WHERE %s' % indicator_q)
        result_max = cursor_max.fetchone()
        results = helper.get_fields(cursor)
        country = {}
        for r in results:

            try:
                country[r['country_id']]['years']
            except:
                loc = r['loc']
                if loc:

                    loc = loc.replace("POINT(", "")
                    loc = loc.replace(")", "")
                    loc_array = loc.split(" ")
                    longitude = loc_array[0]
                    latitude = loc_array[1]
                else:
                    longitude = None
                    latitude = None

                country[r['country_id']] = {'name' : r['country_name'], 'country_id' : r['country_id'], 'longitude' : longitude, 'latitude' : latitude, 'indicator_friendly' : r['friendly_label'], 'type_data' : r['type_data'] , 'indicator' : r['indicator_id'],  'years' : {}}

            year = {}
            year['y' + str(r['year'])] = r['value']
            country[r['country_id']]['years'].update(year)

        country['max_value'] = result_max[0]

        return HttpResponse(ujson.dumps(country), mimetype='application/json')







class IndicatorDataResource(ModelResource):

    class Meta:
        #aid_type is used as dummy
        queryset = AidType.objects.all()
        resource_name = 'indicator-data'
        include_resource_uri = True
        cache = NoTransformCache()


    def get_list(self, request, **kwargs):
        helper = CustomCallHelper()
        city_q = helper.get_and_query(request, 'cities__in', 'city_id')
        country_q = helper.get_and_query(request, 'countries__in', 'c.code')
        region_q = helper.get_and_query(request, 'regions__in', 'r.code')
        year_q = helper.get_and_query(request, 'years__in', 'id.year')
        indicator_q = helper.get_and_query(request, 'indicators__in', 'indicator_id')

        if not indicator_q:
            return HttpResponse(ujson.dumps("No indicator given"), mimetype='application/json')


        filter_string = 'AND (' + city_q + country_q + region_q + year_q + indicator_q + ')'

        if 'AND ()' in filter_string:
            filter_string = filter_string[:-6]

        cursor = connection.cursor()

        cursor.execute('SELECT da.id as indicator_id, da.friendly_label, da.type_data, ci.name as city_name, '
                       'r.code as region_id, r.name as region_name, c.code as country_id, c.name as country_name, '
                       'id.value, id.year, AsText(ci.location) as loc, ci.id as city_id '
                       'FROM indicator_indicatordata id '
                       'LEFT OUTER JOIN geodata_city ci ON id.city_id = ci.id '
                       'LEFT OUTER JOIN geodata_country c ON ci.country_id = c.code '
                       'LEFT OUTER JOIN geodata_region r ON c.region_id = r.code '
                       'LEFT OUTER JOIN indicator_indicator da ON da.id = id.indicator_id '
                       'WHERE id.country_id is null '
                       '%s' % (filter_string))
        desc = cursor.description
        city_results = [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
        ]

        indicator_q = indicator_q.replace(" ) AND (", "")
        print ('SELECT max(value) as max_value FROM indicator_indicatordata WHERE %s GROUP BY indicator_indicatordata.id' % indicator_q)

        cursor_max = connection.cursor()
        cursor_max.execute('SELECT indicator_id, max(value) as max_value FROM indicator_indicatordata WHERE %s GROUP BY indicator_indicatordata.indicator_id' % indicator_q)
        desc = cursor_max.description
        max_results = [
        dict(zip([col[0] for col in desc], row))
        for row in cursor_max.fetchall()
        ]



        # country indicator data
        filter_string = 'AND (' + country_q + region_q + year_q + indicator_q + ')'

        if 'AND ()' in filter_string:
            filter_string = filter_string[:-6]

        cursor = connection.cursor()

        cursor.execute('SELECT da.id as indicator_id, da.friendly_label, da.type_data,  '
                       'r.code as region_id, r.name as region_name, c.code as country_id, c.name as country_name, '
                       'id.value, id.year, AsText(c.center_longlat) as loc '
                       'FROM indicator_indicatordata id '
                       'LEFT OUTER JOIN geodata_country c ON id.country_id = c.code '
                       'LEFT OUTER JOIN geodata_region r ON c.region_id = r.code '
                       'LEFT OUTER JOIN indicator_indicator da ON da.id = id.indicator_id '
                       'WHERE id.city_id is null '
                       '%s' % (filter_string))
        desc = cursor.description
        country_results = [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
        ]

        # region indicator data
        # NOT IMPLEMENTED YET -> WE DO NOT HAVE CENTER LOCATIONS FOR REGIONS

        geolocs = {}
        for r in city_results:

            try:
                geolocs[r['indicator_id']]['cities'][r['city_id']]['years']
            except:

                loc = r['loc']
                if loc:

                    loc = loc.replace("POINT(", "")
                    loc = loc.replace(")", "")
                    loc_array = loc.split(" ")
                    longitude = loc_array[0]
                    latitude = loc_array[1]
                else:
                    longitude = None
                    latitude = None

                if not r['indicator_id'] in geolocs:
                    for mr in max_results:
                        if mr['indicator_id']:
                            max_value = mr['max_value']
                    geolocs[r['indicator_id']] = {'indicator_friendly' : r['friendly_label'], 'type_data' : r['type_data'] , 'indicator' : r['indicator_id'], 'max_value' : max_value, 'cities' : {}, 'countries' : {}}


                geolocs[r['indicator_id']]['cities'][r['city_id']] = {'name' : r['city_name'], 'id' : r['city_id'], 'longitude' : longitude, 'latitude' : latitude, 'years' : {}}

            geolocs[r['indicator_id']]['cities'][r['city_id']]['years'][r['year']] = r['value']


        for c in country_results:

            try:
                geolocs[c['indicator_id']]['countries'][c['country_id']]['years']
            except:

                loc = c['loc']
                if loc:

                    loc = loc.replace("POINT(", "")
                    loc = loc.replace(")", "")
                    loc_array = loc.split(" ")
                    longitude = loc_array[0]
                    latitude = loc_array[1]
                else:
                    longitude = None
                    latitude = None

                if not c['indicator_id'] in geolocs:
                    for mr in max_results:
                        if mr['indicator_id']:
                            max_value = mr['max_value']
                    geolocs[c['indicator_id']] = {'indicator_friendly' : c['friendly_label'], 'type_data' : c['type_data'] , 'indicator' : c['indicator_id'], 'max_value' : max_value, 'cities' : {}, 'countries' : {}}


                geolocs[c['indicator_id']]['countries'][c['country_id']] = {'name' : c['country_name'], 'id' : c['country_id'], 'longitude' : longitude, 'latitude' : latitude, 'years' : {}}

            geolocs[c['indicator_id']]['countries'][c['country_id']]['years'][c['year']] = c['value']






        return HttpResponse(ujson.dumps(geolocs), mimetype='application/json')





















class IndicatorRegionFilterOptionsResource(ModelResource):

    class Meta:
        #aid_type is used as dummy
        queryset = AidType.objects.all()
        resource_name = 'indicator-region-filter-options'
        include_resource_uri = True
        cache = NoTransformCache()


    def get_list(self, request, **kwargs):
        helper = CustomCallHelper()
        region_q = helper.get_and_query(request, 'regions__in', 'region.code')
        indicator_q = helper.get_and_query(request, 'indicators__in', 'i.indicator_id')


        filter_string = ' AND (' + region_q + indicator_q + ')'
        if 'AND ()' in filter_string:
            filter_string = filter_string[:-6]
        cursor = connection.cursor()
        cursor.execute('SELECT DISTINCT i.indicator_id ,ind.friendly_label,region.code as region_id, region.name as region_name '
                       'FROM indicator_indicatordata i '
                       'JOIN indicator_indicator ind ON i.indicator_id = ind.id '
                       'LEFT OUTER JOIN geodata_region region on i.region_id = region.code '
                       'WHERE 1 %s' % (filter_string))

        desc = cursor.description
        results = [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
        ]

        regions = {}
        countries = {}
        indicators = {}
        jsondata = {}

        for r in results:

            region = {}
            if r['region_id']:
                region[r['region_id']] = r['region_name']
                regions.update(region)

            indicator = {}
            if r['indicator_id']:
                indicator[r['indicator_id']] = r['friendly_label']
                indicators.update(indicator)

        jsondata['regions'] = regions
        jsondata['indicators'] = indicators

        return HttpResponse(ujson.dumps(jsondata), mimetype='application/json')


class IndicatorCountryFilterOptionsResource(ModelResource):

    class Meta:
        #aid_type is used as dummy
        queryset = AidType.objects.all()
        resource_name = 'indicator-country-filter-options'
        include_resource_uri = True
        cache = NoTransformCache()


    def get_list(self, request, **kwargs):
        helper = CustomCallHelper()
        country_q = helper.get_and_query(request, 'countries__in', 'country.code')
        region_q = helper.get_and_query(request, 'regions__in', 'region.code')
        indicator_q = helper.get_and_query(request, 'indicators__in', 'i.indicator_id')


        filter_string = ' AND (' + country_q + region_q + indicator_q + ')'
        if 'AND ()' in filter_string:
            filter_string = filter_string[:-6]
        cursor = connection.cursor()
        cursor.execute('SELECT DISTINCT i.indicator_id, ind.friendly_label, country.code as country_id, country.name as country_name, region.code as region_id, region.name as region_name '
                       'FROM indicator_indicatordata i '
                       'JOIN indicator_indicator ind ON i.indicator_id = ind.id '
                       'LEFT OUTER JOIN geodata_country country on i.country_id = country.code '
                       'LEFT OUTER JOIN geodata_region region on country.region_id = region.code '
                       'WHERE 1 %s' % (filter_string))

        results = helper.get_fields(cursor)
        regions = {}
        countries = {}
        indicators = {}
        jsondata = {}

        for r in results:

            region = {}
            if r['region_id']:
                region[r['region_id']] = r['region_name']
                regions.update(region)

            country = {}
            if r['country_id']:
                country[r['country_id']] = r['country_name']
                countries.update(country)

            indicator = {}
            if r['indicator_id']:
                indicator[r['indicator_id']] = r['friendly_label']
                indicators.update(indicator)

        jsondata['regions'] = regions
        jsondata['countries'] = countries
        jsondata['indicators'] = indicators

        return HttpResponse(ujson.dumps(jsondata), mimetype='application/json')



class IndicatorCityFilterOptionsResource(ModelResource):

    class Meta:
        #aid_type is used as dummy
        queryset = AidType.objects.all()
        resource_name = 'indicator-city-filter-options'
        include_resource_uri = True
        cache = NoTransformCache()


    def get_list(self, request, **kwargs):
        helper = CustomCallHelper()
        city_q = helper.get_and_query(request, 'cities__in', 'city.id')
        country_q = helper.get_and_query(request, 'countries__in', 'country.code')
        region_q = helper.get_and_query(request, 'regions__in', 'region.code')
        indicator_q = helper.get_and_query(request, 'indicators__in', 'i.indicator_id')

        filter_string = ' AND (' + city_q + country_q + region_q + indicator_q + ')'
        if 'AND ()' in filter_string:
            filter_string = filter_string[:-6]
        cursor = connection.cursor()


        cursor.execute('SELECT DISTINCT i.indicator_id ,ind.friendly_label, city.id as city_id, city.name as city_name, country.code as country_id, country.name as country_name, region.code as region_id, region.name as region_name '
                       'FROM indicator_indicatordata i '
                       'JOIN indicator_indicator ind ON i.indicator_id = ind.id '
                       'JOIN geodata_city city ON i.city_id=city.id '
                       'LEFT OUTER JOIN geodata_country country on city.country_id = country.code '
                       'LEFT OUTER JOIN geodata_region region on country.region_id = region.code '
                       'WHERE 1 %s' % (filter_string))

        desc = cursor.description
        results = [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
        ]

        regions = {}
        countries = {}
        cities = {}
        indicators = {}
        jsondata = {}

        for r in results:

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

            indicator = {}
            if r['indicator_id']:
                indicator[r['indicator_id']] = r['friendly_label']
                indicators.update(indicator)

        jsondata['regions'] = regions
        jsondata['countries'] = countries
        jsondata['cities'] = cities
        jsondata['indicators'] = indicators

        return HttpResponse(ujson.dumps(jsondata), mimetype='application/json')




class IndicatorFilterOptionsResource(ModelResource):

    class Meta:
        #aid_type is used as dummy
        queryset = AidType.objects.all()
        resource_name = 'indicator-filter-options'
        include_resource_uri = True
        cache = NoTransformCache()


    def get_list(self, request, **kwargs):
        helper = CustomCallHelper()
        city_q = helper.get_and_query(request, 'cities__in', 'city.id')
        country_q = helper.get_and_query(request, 'countries__in', 'country.code')
        region_q = helper.get_and_query(request, 'regions__in', 'region.code')
        indicator_q = helper.get_and_query(request, 'indicators__in', 'i.indicator_id')
    

        filter_string = ' AND (' + city_q + country_q + region_q + indicator_q + ')'
        if 'AND ()' in filter_string:
            filter_string = filter_string[:-6]
        cursor = connection.cursor()

        # city filters
        cursor.execute('SELECT DISTINCT i.indicator_id ,ind.friendly_label, city.id as city_id, city.name as city_name, country.code as country_id, country.name as country_name, region.code as region_id, region.name as region_name '
                       'FROM indicator_indicatordata i '
                       'JOIN indicator_indicator ind ON i.indicator_id = ind.id '
                       'JOIN geodata_city city ON i.city_id=city.id '
                       'LEFT OUTER JOIN geodata_country country on city.country_id = country.code '
                       'LEFT OUTER JOIN geodata_region region on country.region_id = region.code '
                       'WHERE 1 %s' % (filter_string))

        desc = cursor.description
        city_results = [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
        ]

        # country filters
        filter_string = ' AND (' + country_q + region_q + indicator_q + ')'
        if 'AND ()' in filter_string:
            filter_string = filter_string[:-6]
        cursor = connection.cursor()
        cursor.execute('SELECT DISTINCT i.indicator_id, ind.friendly_label, country.code as country_id, country.name as country_name, region.code as region_id, region.name as region_name '
                       'FROM indicator_indicatordata i '
                       'JOIN indicator_indicator ind ON i.indicator_id = ind.id '
                       'LEFT OUTER JOIN geodata_country country on i.country_id = country.code '
                       'LEFT OUTER JOIN geodata_region region on country.region_id = region.code '
                       'WHERE 1 %s' % (filter_string))

        desc = cursor.description
        country_results = [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
        ]

        # region filters
        filter_string = ' AND (' + region_q + indicator_q + ')'
        if 'AND ()' in filter_string:
            filter_string = filter_string[:-6]
        cursor = connection.cursor()
        cursor.execute('SELECT DISTINCT i.indicator_id ,ind.friendly_label,region.code as region_id, region.name as region_name '
                       'FROM indicator_indicatordata i '
                       'JOIN indicator_indicator ind ON i.indicator_id = ind.id '
                       'LEFT OUTER JOIN geodata_region region on i.region_id = region.code '
                       'WHERE 1 %s' % (filter_string))

        desc = cursor.description
        region_results = [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
        ]

        regions = {}
        countries = {}
        cities = {}
        indicators = {}
        jsondata = {}

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

            indicator = {}
            if r['indicator_id']:
                indicator[r['indicator_id']] = r['friendly_label']
                indicators.update(indicator)

        for r in country_results:

            region = {}
            if r['region_id']:
                region[r['region_id']] = r['region_name']
                regions.update(region)

            country = {}
            if r['country_id']:
                country[r['country_id']] = r['country_name']
                countries.update(country)

            indicator = {}
            if r['indicator_id']:
                indicator[r['indicator_id']] = r['friendly_label']
                indicators.update(indicator)

        for r in region_results:

            region = {}
            if r['region_id']:
                region[r['region_id']] = r['region_name']
                regions.update(region)

            indicator = {}
            if r['indicator_id']:
                indicator[r['indicator_id']] = r['friendly_label']
                indicators.update(indicator)

        jsondata['regions'] = regions
        jsondata['countries'] = countries
        jsondata['cities'] = cities
        jsondata['indicators'] = indicators

        return HttpResponse(ujson.dumps(jsondata), mimetype='application/json')