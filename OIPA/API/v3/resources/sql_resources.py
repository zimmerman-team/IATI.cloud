# Tastypie specific
from tastypie.resources import ModelResource

# Data specific
from geodata.data_backup.country_data import countryData

# Cache specific
from API.cache import NoTransformCache
from IATI.models import aid_type
from Cache.validator import Validator


# Direct sql specific
import ujson
from django.db import connection
from django.http import HttpResponse



class CustomCallHelper():

    def make_where_query(self, values, name):
        query = ''
        if values:
            if not values[0]:
                return None

            for v in values:
                query += '  ' + name + ' = "' + v +'" OR'
            query = query[:-2]
        return query

    def get_and_query(self, request, parameter, queryparameter):

        filters = request.GET.get(parameter, None)
        if filters:
            query = self.make_where_query(values=filters.split(','), name=queryparameter)
            query += ') AND ('
        else:
            query = ''
        return query

    def get_fields(self, cursor):
        desc = cursor.description
        results = [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
        ]
        return results

    def get_filter_query(self, filters):
        q= ''

        for f in filters:
            if f[f.keys()[0]]:
                values = f[f.keys()[0]].split(',')
            else:
                values = None
            q += self.make_where_query(values=values, name=f.keys()[0]) + ') and ('

        q = q.replace(' and ()', '')
        q = q[:-5]
        q = " AND (" + q
        try:
            q[8]
            return q
        except IndexError:
            return ''

    def find_polygon(self, iso2):
        polygon = None
        for k in countryData['features']:
            try:
                if k['properties']['iso2'] == iso2:
                    polygon = k['geometry']
            except KeyError:
                pass
        if not polygon:
            polygon = {
                "type" : "Polygon",
                "coordinates" : []
            }

        return polygon




class ActivityFilterOptionsResource(ModelResource):

    class Meta:
        #aid_type is used as dummy
        queryset = aid_type.objects.all()
        resource_name = 'activity-filter-options'
        include_resource_uri = True
        cache = NoTransformCache()


    def get_list(self, request, **kwargs):

        validator = Validator()
        cururl = request.META['PATH_INFO'] + "?" + request.META['QUERY_STRING']
        if validator.is_cached(cururl):
            return HttpResponse(validator.get_cached_call(cururl), mimetype='application/json')

        helper = CustomCallHelper()
        cursor = connection.cursor()
        organisations = request.GET.get("reporting_organisation__in", None)
        if organisations:
            q_organisations = 'WHERE a.reporting_organisation_id = "' + organisations + '"'
        else:
            q_organisations = ""

        cursor.execute('SELECT c.code, c.name, count(c.code) as total_amount '
                       'FROM geodata_country c '
                       'LEFT JOIN IATI_activity_recipient_country rc on c.code = rc.country_id '
                       'LEFT JOIN IATI_activity a on rc.activity_id = a.id %s '
                       'GROUP BY c.code' % (q_organisations))
        results1 = helper.get_fields(cursor=cursor)
        cursor.execute('SELECT s.code, s.name, count(s.code) as total_amount '
                       'FROM IATI_sector s '
                       'LEFT JOIN IATI_activity_sector as ias on s.code = ias.sector_id '
                       'LEFT JOIN IATI_activity a on ias.activity_id = a.id '
                       '%s '
                       'GROUP BY s.code' % (q_organisations))
        results2 = helper.get_fields(cursor=cursor)
        if q_organisations:
            q_organisations = q_organisations.replace("WHERE", "AND")
        cursor.execute('SELECT r.code, r.name, count(r.code) as total_amount '
                       'FROM geodata_region r '
                       'LEFT JOIN IATI_activity_recipient_region rr on r.code = rr.region_id '
                       'LEFT JOIN IATI_activity a on rr.activity_id = a.id '
                       'WHERE r.source = "DAC" '
                       '%s '
                       'GROUP BY r.code' % (q_organisations))
        results3 = helper.get_fields(cursor=cursor)



        options = {}
        options['countries'] = {}
        options['regions'] = {}
        options['sectors'] = {}

        for r in results1:

            country_item = {}
            country_item['name'] = r['name']
            country_item['total'] = r['total_amount']
            options['countries'][r['code']] = country_item

        for r in results2:
            sector_item = {}
            sector_item['name'] = r['name']
            sector_item['total'] = r['total_amount']
            options['sectors'][r['code']] = sector_item

        for r in results3:

            region_item = {}
            region_item['name'] = r['name']
            region_item['total'] = r['total_amount']
            options['regions'][r['code']] = region_item



        if not q_organisations:
            cursor.execute('SELECT a.reporting_organisation_id, o.name, count(a.reporting_organisation_id) as total_amount '
                       'FROM IATI_activity a '
                       'INNER JOIN IATI_organisation o on a.reporting_organisation_id = o.code '
                       'GROUP BY a.reporting_organisation_id')
            results4 = helper.get_fields(cursor=cursor)

            options['reporting_organisations'] = {}

            for r in results4:

                org_item = {}
                org_item['name'] = r['name']
                org_item['total'] = r['total_amount']
                options['reporting_organisations'][r['reporting_organisation_id']] = org_item

        return HttpResponse(ujson.dumps(options), mimetype='application/json')






class IndicatorCountryDataResource(ModelResource):

    class Meta:
        #aid_type is used as dummy
        queryset = aid_type.objects.all()
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
                       'FROM indicators_indicator_data id '
                       'JOIN geodata_country c ON id.country_id = c.code '
                       'JOIN indicators_indicator da ON da.id = id.indicator_id WHERE %s' % (filter_string))
        cursor_max = connection.cursor()

        indicator_q = indicator_q.replace(" ) AND (", "")
        cursor_max.execute('SELECT max(value) as max_value FROM indicators_indicator_data WHERE %s' % indicator_q)
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
        queryset = aid_type.objects.all()
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
                       'FROM indicators_indicator_data id '
                       'JOIN geodata_city ci ON id.city_id = ci.id '
                       'JOIN geodata_country c ON ci.country_id = c.code '
                       'JOIN geodata_region r ON c.region_id = r.code '
                       'JOIN indicators_indicator da ON da.id = id.indicator_id WHERE %s' % (filter_string))


        cursor_max = connection.cursor()
        indicator_q = indicator_q.replace(" ) AND (", "")
        cursor_max.execute('SELECT max(value) as max_value FROM indicators_indicator_data WHERE %s' % indicator_q)
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
        queryset = aid_type.objects.all()
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
                       'FROM indicators_indicator_data id '
                       'LEFT OUTER JOIN geodata_city c ON id.country_id = c.code '
                       'JOIN indicators_indicator da ON da.id = id.indicator_id WHERE %s' % (filter_string))
        cursor_max = connection.cursor()

        indicator_q = indicator_q.replace(" ) AND (", "")
        cursor_max.execute('SELECT max(value) as max_value FROM indicators_indicator_data WHERE %s' % indicator_q)
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



class IndicatorRegionFilterOptionsResource(ModelResource):

    class Meta:
        #aid_type is used as dummy
        queryset = aid_type.objects.all()
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
                       'FROM indicators_indicator_data i '
                       'JOIN indicators_indicator ind ON i.indicator_id = ind.id '
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


class IndicatorCountryFilterOptionsResource(ModelResource):

    class Meta:
        #aid_type is used as dummy
        queryset = aid_type.objects.all()
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
                       'FROM indicators_indicator_data i '
                       'JOIN indicators_indicator ind ON i.indicator_id = ind.id '
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
        queryset = aid_type.objects.all()
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
                       'FROM indicators_indicator_data i '
                       'JOIN indicators_indicator ind ON i.indicator_id = ind.id '
                       'LEFT OUTER JOIN geodata_city city ON i.city_id=city.id '
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








class CountryGeojsonResource(ModelResource):

    class Meta:
        #aid_type is used as dummy
        queryset = aid_type.objects.all()
        resource_name = 'country-geojson'
        include_resource_uri = True
        cache = NoTransformCache()


    def get_list(self, request, **kwargs):

        validator = Validator()
        cururl = request.META['PATH_INFO'] + "?" + request.META['QUERY_STRING']
        if validator.is_cached(cururl):
            return HttpResponse(validator.get_cached_call(cururl), mimetype='application/json')

        helper = CustomCallHelper()
        country_q = helper.get_and_query(request, 'countries__in', 'c.code')
        budget_q = request.GET.get('budgets__in', None)
        region_q = helper.get_and_query(request, 'regions__in', 'r.code')
        sector_q = helper.get_and_query(request, 'sectors__in', 's.sector_id')
        organisation_q = helper.get_and_query(request, 'reporting_organisation__in', 'a.reporting_organisation_id')

        filter_string = ' AND (' + country_q + organisation_q + region_q + sector_q + ')'
        if 'AND ()' in filter_string:
            filter_string = filter_string[:-6]

        if budget_q:
            filter_string += ' AND total_budget > ' + budget_q + ' '

        if region_q:
            filter_region = 'LEFT JOIN IATI_activity_recipient_region rr ON rr.activity_id = a.id LEFT JOIN geodata_region r ON rr.region_id = r.code '
        else:
            filter_region = ''

        if sector_q:
            filter_sector = 'LEFT JOIN IATI_activity_sector s ON a.id = s.activity_id '
        else:
            filter_sector = ''

        cursor = connection.cursor()
        query = 'SELECT c.code as country_id, c.name as country_name, count(a.id) as total_projects '\
                'FROM IATI_activity a '\
                'LEFT JOIN IATI_activity_recipient_country rc ON rc.activity_id = a.id '\
                'LEFT JOIN geodata_country c ON rc.country_id = c.code '\
                '%s %s'\
                'WHERE 1 %s'\
                'GROUP BY c.code' % (filter_region, filter_sector, filter_string)
        cursor.execute(query)

        activity_result = {'type' : 'FeatureCollection', 'features' : []}

        activities = []

        results = helper.get_fields(cursor=cursor)
        for r in results:
            country = {}
            country['type'] = 'Feature'
            country['id'] = r['country_id']

            country['properties'] = {'name' : r['country_name'], 'project_amount' : r['total_projects']}
            country['geometry'] = helper.find_polygon(r['country_id'])

            activities.append(country)

        result = {}

        activity_result['features'] = activities
        return HttpResponse(ujson.dumps(activity_result), mimetype='application/json')



class Adm1rRegionGeojsonResource(ModelResource):

    class Meta:
        #aid_type is used as dummy
        queryset = aid_type.objects.all()
        resource_name = 'adm1-region-geojson'
        include_resource_uri = True
        cache = NoTransformCache()


    def get_list(self, request, **kwargs):
        helper = CustomCallHelper()
        country_id = request.GET.get("country_id", None)

        cursor = connection.cursor()

        cursor.execute('SELECT r.adm1_code, r.name, r.polygon, r.geometry_type  '\
                'FROM geodata_adm1_region r '\
                'WHERE r.country_id = "%s"' % (country_id))

        activity_result = {'type' : 'FeatureCollection', 'features' : []}

        activities = []

        results = helper.get_fields(cursor=cursor)
        for r in results:
            region = {}
            region['type'] = 'Feature'
            region['geometry'] = {'type' : r['geometry_type'], 'coordinates' : r['polygon']}
            region['properties'] = {'id' : r['adm1_code'], 'name' : r['name']}
            activities.append(region)

        result = {}

        activity_result['features'] = activities
        return HttpResponse(ujson.dumps(activity_result), mimetype='application/json')


