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
from api.v3.resources.csv_helper import CsvHelper
from api.v3.resources.custom_call_helper import CustomCallHelper

class ActivityFilterOptionsResource(ModelResource):

    class Meta:
        #aid_type is used as dummy
        queryset = AidType.objects.all()
        resource_name = 'activity-filter-options'
        include_resource_uri = True
        cache = NoTransformCache()
        allowed_methods = ['get']


    def get_list(self, request, **kwargs):

        # check if call is cached using validator.is_cached
        # check if call contains flush, if it does the call comes from the cache updater and shouldn't return cached results
        validator = Validator()
        cururl = request.META['PATH_INFO'] + "?" + request.META['QUERY_STRING']

        if not 'flush' in cururl and validator.is_cached(cururl):
            return HttpResponse(validator.get_cached_call(cururl), content_type='application/json')


        helper = CustomCallHelper()
        cursor = connection.cursor()
        organisations = request.GET.get("reporting_organisation__in", None)
        include_donors = request.GET.get("include_donor", None)
        include_start_year_actual = request.GET.get("include_start_year_actual", None)
        include_start_year_planned = request.GET.get("include_start_year_planned", None)
        if organisations:
            q_organisations = 'WHERE a.reporting_organisation_id = "' + organisations + '"'
        else:
            q_organisations = ""

        cursor.execute('SELECT c.code, c.name, count(c.code) as total_amount '
                       'FROM geodata_country c '
                       'LEFT JOIN iati_activityrecipientcountry rc on c.code = rc.country_id '
                       'LEFT JOIN iati_activity a on rc.activity_id = a.id %s '
                       'GROUP BY c.code' % (q_organisations))
        results1 = helper.get_fields(cursor=cursor)
        cursor.execute('SELECT s.code, s.name, count(s.code) as total_amount '
                       'FROM iati_sector s '
                       'LEFT JOIN iati_activitysector as ias on s.code = ias.sector_id '
                       'LEFT JOIN iati_activity a on ias.activity_id = a.id '
                       '%s '
                       'GROUP BY s.code' % (q_organisations))
        results2 = helper.get_fields(cursor=cursor)
        if q_organisations:
            q_organisations = q_organisations.replace("WHERE", "AND")
        cursor.execute('SELECT r.code, r.name, count(r.code) as total_amount '
                       'FROM geodata_region r '
                       'LEFT JOIN iati_activityrecipientregion rr on r.code = rr.region_id '
                       'LEFT JOIN iati_activity a on rr.activity_id = a.id '
                       'WHERE r.region_vocabulary_id = 1 '
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

        if include_donors:
            options['donors'] = {}

            cursor.execute('SELECT o.code, o.name, count(o.code) as total_amount '
                       'FROM iati_activity a '
                       'JOIN iati_activityparticipatingorganisation as po on a.id = po.activity_id '
                       'JOIN iati_organisation as o on po.organisation_id = o.code '
                       'WHERE 1 %s '
                       'GROUP BY o.code' % (q_organisations))
            results4 = helper.get_fields(cursor=cursor)

            for r in results4:

                donor_item = {}
                donor_item['name'] = r['name']
                donor_item['total'] = r['total_amount']
                options['donors'][r['code']] = donor_item

        if include_start_year_actual:

            options['start_actual'] = {}
            cursor.execute('SELECT YEAR(a.start_actual) as start_year, count(YEAR(a.start_actual)) as total_amount '
                       'FROM iati_activity a '
                       'WHERE 1 %s '
                       'GROUP BY YEAR(a.start_actual)' % (q_organisations))
            results5 = helper.get_fields(cursor=cursor)

            for r in results5:
                start_actual_item = {}
                start_actual_item['name'] = r['start_year']
                start_actual_item['total'] = r['total_amount']
                options['start_actual'][r['start_year']] = start_actual_item

        if include_start_year_planned:

            options['start_planned_years'] = {}
            cursor.execute('SELECT YEAR(a.start_planned) as start_year, count(YEAR(a.start_planned)) as total_amount '
                       'FROM iati_activity a '
                       'WHERE 1 %s '
                       'GROUP BY YEAR(a.start_planned)' % (q_organisations))
            results5 = helper.get_fields(cursor=cursor)

            for r in results5:
                start_planned_item = {}
                start_planned_item['name'] = r['start_year']
                start_planned_item['total'] = r['total_amount']
                options['start_planned_years'][r['start_year']] = start_planned_item


        if not q_organisations:
            cursor.execute('SELECT a.reporting_organisation_id, o.name, count(a.reporting_organisation_id) as total_amount '
                       'FROM iati_activity a '
                       'INNER JOIN iati_organisation o on a.reporting_organisation_id = o.code '
                       'GROUP BY a.reporting_organisation_id')
            results4 = helper.get_fields(cursor=cursor)

            options['reporting_organisations'] = {}

            for r in results4:

                org_item = {}
                org_item['name'] = r['name']
                org_item['total'] = r['total_amount']
                options['reporting_organisations'][r['reporting_organisation_id']] = org_item

        return HttpResponse(ujson.dumps(options), content_type='application/json')


class ActivityFilterOptionsUnescoResource(ModelResource):

    class Meta:
        #aid_type is used as dummy
        queryset = AidType.objects.all()
        resource_name = 'activity-filter-options-unesco'
        include_resource_uri = True
        cache = NoTransformCache()
        allowed_methods = ['get']


    def get_list(self, request, **kwargs):

        # check if call is cached using validator.is_cached
        # check if call contains flush, if it does the call comes from the cache updater and shouldn't return cached results
        validator = Validator()
        cururl = request.META['PATH_INFO'] + "?" + request.META['QUERY_STRING']

        if not 'flush' in cururl and validator.is_cached(cururl):
            return HttpResponse(validator.get_cached_call(cururl), content_type='application/json')


        helper = CustomCallHelper()
        cursor = connection.cursor()
        organisations = request.GET.get("reporting_organisation__in", None)

        countries = request.GET.get("countries__in", None)

        perspective = request.GET.get("perspective", None)
        w_perspective = ''

        if perspective:
            if perspective == 'country':
                q_perspective = ' JOIN iati_activityrecipientcountry as c on a.id = c.activity_id '
            elif perspective == 'region':
                q_perspective = ' JOIN iati_activityrecipientregion as r on a.id = r.activity_id '
            elif perspective == 'global':
                q_perspective = ''
                w_perspective = 'AND a.scope_id = 1 '
            else:
                q_perspective = ''
        else:
            q_perspective = ''


        include_donors = request.GET.get("include_donor", None)
        include_start_year_actual = request.GET.get("include_start_year_actual", None)
        include_start_year_planned = request.GET.get("include_start_year_planned", None)
        if organisations:
            q_organisations = 'AND a.reporting_organisation_id = "' + organisations + '" '
        else:
            q_organisations = ""

        query = ('SELECT c.code, c.name, count(c.code) as total_amount '
                       'FROM geodata_country c '
                       'LEFT JOIN iati_activityrecipientcountry rc on c.code = rc.country_id '
                       'LEFT JOIN iati_activity a on rc.activity_id = a.id '
                       'WHERE 1 %s %s '
                       'GROUP BY c.code' % (q_organisations, w_perspective))

        #making query for country results
        cursor.execute('SELECT c.code, c.name, count(c.code) as total_amount '
                       'FROM geodata_country c '
                       'LEFT JOIN iati_activityrecipientcountry rc on c.code = rc.country_id '
                       'LEFT JOIN iati_activity a on rc.activity_id = a.id '
                       'WHERE 1 %s %s '
                       'GROUP BY c.code' % (q_organisations, w_perspective))
        results1 = helper.get_fields(cursor=cursor)

        #making query for sector results
        cursor.execute('SELECT s.code, s.name, count(s.code) as total_amount '
                       'FROM iati_sector s '
                       'LEFT JOIN iati_activitysector as ias on s.code = ias.sector_id '
                       'LEFT JOIN iati_activity a on ias.activity_id = a.id '
                       'WHERE 1 %s %s '
                       'GROUP BY s.code' % (q_organisations, w_perspective))
        results2 = helper.get_fields(cursor=cursor)

        #making query for regions
        if q_organisations:
            q_organisations = q_organisations.replace("WHERE", "AND")
        cursor.execute('SELECT r.code, r.name, count(r.code) as total_amount '
                       'FROM geodata_region r '
                       'LEFT JOIN iati_activityrecipientregion rr on r.code = rr.region_id '
                       'LEFT JOIN iati_activity a on rr.activity_id = a.id '
                       'WHERE r.region_vocabulary_id = 1 '
                       '%s %s '
                       'GROUP BY r.code' % (q_organisations, w_perspective))
        results3 = helper.get_fields(cursor=cursor)

        options = {}
        options['countries'] = {}
        options['regions'] = {}
        options['sectors'] = {}


        #country results
        for r in results1:

            country_item = {}
            country_item['name'] = r['name']
            country_item['total'] = r['total_amount']
            options['countries'][r['code']] = country_item
        #sector results
        for r in results2:
            sector_item = {}
            sector_item['name'] = r['name']
            sector_item['total'] = r['total_amount']
            options['sectors'][r['code']] = sector_item
        #region results
        for r in results3:

            region_item = {}
            region_item['name'] = r['name']
            region_item['total'] = r['total_amount']
            options['regions'][r['code']] = region_item
        #donor results
        if include_donors:
            options['donors'] = {}
            if countries:
                q_countries = ' and c.country_id = "' + countries + '"'
            else:
                q_countries = ""

            cursor.execute('SELECT o.code, o.name, count(o.code) as total_amount '
                       'FROM iati_activity a '
                       'JOIN iati_activityparticipatingorganisation as po on a.id = po.activity_id '
                       'JOIN iati_organisation as o on po.organisation_id = o.code '
                       ' %s '
                       'WHERE 1 %s %s %s '
                       'GROUP BY o.code' % (q_perspective, q_organisations, q_countries, w_perspective))
            results4 = helper.get_fields(cursor=cursor)

            for r in results4:

                donor_item = {}
                donor_item['name'] = r['name']
                donor_item['total'] = r['total_amount']
                options['donors'][r['code']] = donor_item

        if include_start_year_actual:

            options['start_actual'] = {}
            cursor.execute('SELECT YEAR(a.start_actual) as start_year, count(YEAR(a.start_actual)) as total_amount '
                       'FROM iati_activity a '
                        ' %s '
                       'WHERE 1 %s %s '
                       'GROUP BY YEAR(a.start_actual)' % (q_perspective, q_organisations, w_perspective))
            results5 = helper.get_fields(cursor=cursor)

            for r in results5:
                start_actual_item = {}
                start_actual_item['name'] = r['start_year']
                start_actual_item['total'] = r['total_amount']
                options['start_actual'][r['start_year']] = start_actual_item

        if include_start_year_planned:

            options['start_planned_years'] = {}
            cursor.execute('SELECT YEAR(a.start_planned) as start_year, count(YEAR(a.start_planned)) as total_amount '
                       'FROM iati_activity a '
                        ' %s '
                       'WHERE 1 %s %s '
                       'GROUP BY YEAR(a.start_planned)' % (q_perspective, q_organisations, w_perspective))
            results5 = helper.get_fields(cursor=cursor)

            for r in results5:
                start_planned_item = {}
                start_planned_item['name'] = r['start_year']
                start_planned_item['total'] = r['total_amount']
                options['start_planned_years'][r['start_year']] = start_planned_item


        if not q_organisations:
            cursor.execute('SELECT a.reporting_organisation_id, o.name, count(a.reporting_organisation_id) as total_amount '
                       'FROM iati_activity a '
                        ' %s '
                       'INNER JOIN iati_organisation o on a.reporting_organisation_id = o.code '
                       'WHERE 1 %s '
                       'GROUP BY a.reporting_organisation_id' % q_perspective, w_perspective)
            results4 = helper.get_fields(cursor=cursor)

            options['reporting_organisations'] = {}

            for r in results4:

                org_item = {}
                org_item['name'] = r['name']
                org_item['total'] = r['total_amount']
                options['reporting_organisations'][r['reporting_organisation_id']] = org_item

        return HttpResponse(ujson.dumps(options), content_type='application/json')



class CountryGeojsonResource(ModelResource):

    class Meta:
        #aid_type is used as dummy
        queryset = AidType.objects.all()
        resource_name = 'country-geojson'
        include_resource_uri = True
        cache = NoTransformCache()
        allowed_methods = ['get']


    def get_list(self, request, **kwargs):

        # check if call is cached using validator.is_cached
        # check if call contains flush, if it does the call comes from the cache updater and shouldn't return cached results
        validator = Validator()
        cururl = request.META['PATH_INFO'] + "?" + request.META['QUERY_STRING']

        if not 'flush' in cururl and validator.is_cached(cururl):
            return HttpResponse(validator.get_cached_call(cururl), content_type='application/json')

        helper = CustomCallHelper()
        country_q = helper.get_and_query(request, 'countries__in', 'c.code')
        budget_q_gte = request.GET.get('total_budget__gt', None)
        budget_q_lte = request.GET.get('total_budget__lt', None)
        region_q = helper.get_and_query(request, 'regions__in', 'r.code')
        sector_q = helper.get_and_query(request, 'sectors__in', 's.sector_id')
        donor_q = helper.get_and_query(request, 'participating_organisations__organisation__code__in', 'apo.organisation_id')
        organisation_q = helper.get_and_query(request, 'reporting_organisation__in', 'a.reporting_organisation_id')
        budget_q = ''
        country_query = request.GET.get("country", None)
        project_query = request.GET.get("query", None)
        result_title_q = helper.get_and_query(request, 'result_title', 'r.title')

        if budget_q_gte:
            budget_q += ' a.total_budget > "' + budget_q_gte + '" ) AND ('
        if budget_q_lte:
            budget_q += ' a.total_budget < "' + budget_q_lte + '" ) AND ('

        filter_string = ' AND (' + country_q + organisation_q + region_q + sector_q + budget_q + result_title_q + ')'
        if 'AND ()' in filter_string:
            filter_string = filter_string[:-6]

        if region_q:
            filter_region = 'LEFT JOIN iati_activityrecipientregion rr ON rr.activity_id = a.id LEFT JOIN geodata_region r ON rr.region_id = r.code '
        else:
            filter_region = ''

        if sector_q:
            filter_sector = 'LEFT JOIN iati_activitysector s ON a.id = s.activity_id '
        else:
            filter_sector = ''

        filter_result = ''
        if result_title_q:
            filter_result = 'LEFT JOIN iati_result r ON a.id = r.activity_id '

        filter_donor = ''
        if donor_q:
            filter_donor = 'LEFT JOIN iati_activityparticipatingorganisation as apo on a.id = apo.activity_id '
            filter_string += ' AND apo.role_id = "Funding" '

        if country_query:
            filter_string += 'AND c.name LIKE "%%' + country_query + '%%" '

        filter_project_query = ''
        if project_query:
            filter_project_query = 'LEFT JOIN iati_title as t on a.id = t.activity_id '
            filter_string += 'AND ( t.title LIKE "%%' + project_query + '%%" OR c.name LIKE "%%' + project_query + '%%" ) '

        cursor = connection.cursor()
        query = 'SELECT c.code as country_id, c.name as country_name, count(a.id) as total_projects '\
                'FROM iati_activity a '\
                'LEFT JOIN iati_activityrecipientcountry rc ON rc.activity_id = a.id '\
                'LEFT JOIN geodata_country c ON rc.country_id = c.code '\
                '%s %s %s %s %s '\
                'WHERE 1 %s'\
                'GROUP BY c.code' % (filter_region, filter_sector, filter_result, filter_donor, filter_project_query, filter_string)

        cursor.execute(query)

        activity_result = {'type': 'FeatureCollection', 'features': []}

        activities = []

        results = helper.get_fields(cursor=cursor)
        for r in results:
            country = {}
            country['type'] = 'Feature'
            country['id'] = r['country_id']

            country['properties'] = {'name': r['country_name'], 'project_amount': r['total_projects']}
            country['geometry'] = helper.find_polygon(r['country_id'])

            activities.append(country)

        activity_result['features'] = activities
        return HttpResponse(ujson.dumps(activity_result), content_type='application/json')


def dict2xml(d, root_node, first, listname):
        wrap          =     False if None == root_node or isinstance(d, list) else True
        root          = 'objects' if None == root_node else root_node
        root_singular = root[:-1] if 's' == root[-1] and None == root_node else root
        xml           = ''
        children      = []

        if isinstance(d, dict):
            for key, value in dict.items(d):
                if isinstance(value, dict):
                    children.append(dict2xml(value, key, False, listname))
                elif isinstance(value, list):
                    children.append(dict2xml(value, key, False, listname))
                else:
                    # children.append(str(value), key)
                    xml = xml + '<' + key + '>' + str(value) + '</' + key + '>'
        else:
            if isinstance(d, list):
                for value in d:
                    children.append(dict2xml(value, listname, False, listname))
            else:
                for value in d:
                    children.append(dict2xml(value, root_singular, False, listname))

        end_tag = '>'

        if wrap or isinstance(d, dict):
            if first:
                xml = '<' + root + end_tag + xml
            else:
                xml = '<' + root + end_tag + xml + '</' + root + end_tag

        if 0 < len(children):
            for child in children:
                xml = xml + child

            if wrap or isinstance(d, dict):
                xml = xml + '</' + root + '>'

        return xml



class CountryActivitiesResource(ModelResource):

    class Meta:
        queryset = AidType.objects.none()
        resource_name = 'country-activities'
        include_resource_uri = True
        cache = NoTransformCache()
        serializer = CsvHelper()
        allowed_methods = ['get']

    def get_list(self, request, **kwargs):

        validator = Validator()
        cururl = request.META['PATH_INFO'] + "?" + request.META['QUERY_STRING']
        if not 'flush' in cururl and validator.is_cached(cururl):
            return HttpResponse(validator.get_cached_call(cururl), content_type='application/json')

        helper = CustomCallHelper()
        country_q = helper.get_and_query(request, 'countries__in', 'c.code')
        budget_q_gte = request.GET.get('total_budget__gt', None)
        budget_q_lte = request.GET.get('total_budget__lt', None)
        region_q = helper.get_and_query(request, 'regions__in', 'r.code')
        sector_q = helper.get_and_query(request, 'sectors__in', 's.sector_id')
        donor_q = helper.get_and_query(request, 'participating_organisations__organisation__code__in', 'apo.organisation_id')
        organisation_q = helper.get_and_query(request, 'reporting_organisation__in', 'a.reporting_organisation_id')
        start_actual_q = helper.get_year_and_query(request, 'start_actual__in', 'a.start_actual')
        start_planned_q = helper.get_year_and_query(request, 'start_planned__in', 'a.start_planned')
        budget_q = ''
        limit = request.GET.get("limit", 999)
        offset = request.GET.get("offset", 0)
        order_by = request.GET.get("order_by", "country_name")
        order_asc_desc = request.GET.get("order_asc_desc", "ASC")
        country_query = request.GET.get("country", None)
        project_query = request.GET.get("query", None)
        total_commitments_q = request.GET.get("total_commitments", None)
        output_format = request.GET.get("format", "json")
        include_unesco_empty = request.GET.get("include_unesco_empty", False)
        result_title_q = helper.get_and_query(request, 'results_title__in', 'r.title')

        if budget_q_gte:
            budget_q += ' a.total_budget > "' + budget_q_gte + '" ) AND ('
        if budget_q_lte:
            budget_q += ' a.total_budget < "' + budget_q_lte + '" ) AND ('

        filter_string = ''.join([
            country_q,
            organisation_q,
            region_q,
            sector_q,
            budget_q,
            start_planned_q,
            start_actual_q,
            donor_q,
            result_title_q
        ])

        if filter_string:
            filter_string = ' AND (' + filter_string[:-7] + ') '

        query_select = [
            'SELECT c.code as country_id',
            'c.name as country_name',
            'AsText(c.center_longlat) as location'
        ]

        query_join = [
            'FROM geodata_country c ',
            'LEFT JOIN iati_activityrecipientcountry rc ON rc.country_id = c.code ',
            'LEFT JOIN iati_activity a ON rc.activity_id = a.id '
        ]

        if total_commitments_q:
            query_join.append('LEFT JOIN iati_transaction tr ON tr.activity_id = a.id ')
            query_select.append('sum(tr.value) as total_commitment')
            query_select.append('count(distinct(a.id)) as total_projects')
            filter_string += ' AND tr.transaction_type_id = "C" '
        else:
            query_select.append('sum(a.total_budget) as total_budget')
            query_select.append('count(a.id) as total_projects',)

        if region_q:
            query_join.append(
                'LEFT JOIN iati_activityrecipientregion rr '
                'ON rr.activity_id = a.id '
                'LEFT JOIN geodata_region r '
                'ON rr.region_id = r.code ')

        if sector_q:
            query_join.append(
                'LEFT JOIN iati_activitysector s '
                'ON a.id = s.activity_id ')

        if donor_q:
            query_join.append(
                'LEFT JOIN iati_activityparticipatingorganisation as apo '
                'ON a.id = apo.activity_id ')
            filter_string += ' AND apo.role_id = "Funding" '

        if country_query:
            filter_string += 'AND c.name LIKE "%%' + country_query + '%%" '

        if project_query:
            query_join.append(
                'LEFT JOIN iati_title as t ON a.id = t.activity_id '
                'LEFT JOIN iati_description as dis ON a.id = dis.activity_id '
                'LEFT JOIN iati_otheridentifier as oa ON a.id = oa.activity_id ')
            filter_string += 'AND ( t.title LIKE "%%' + project_query + '%%" '
            filter_string += 'OR dis.description LIKE "%%' + project_query + '%%" '
            filter_string += 'OR oa.identifier LIKE "%%' + project_query + '%%" '
            filter_string += 'OR c.name LIKE "%%' + project_query + '%%" ) '

        if result_title_q:
            query_join.append(
                'LEFT JOIN iati_result r '
                'ON a.id = r.activity_id ')

        query_end = 'WHERE c.code is not null ' \
                '%s '\
                'GROUP BY c.code ' \
                'ORDER BY %s %s ' \
                'LIMIT %s OFFSET %s' % (filter_string, order_by, order_asc_desc, limit, offset)
        query = ','.join(query_select) + ' ' + ''.join(query_join) + query_end

        if include_unesco_empty and organisation_q:
            query = query.replace(organisation_q, "")
            query = query.replace(' AND (' + organisation_q[:-6], "")
            query = query.replace(organisation_q[:-6], "")
            query = query.replace(
                "LEFT JOIN iati_activity a ON rc.activity_id = a.id",
                "LEFT JOIN iati_activity a ON rc.activity_id = a.id AND " + organisation_q[:-8])
            query = query.replace("WHERE ", "WHERE unesco_region_id is not null AND ")
        cursor = connection.cursor()
        cursor.execute(query)

        activities = []
        results = helper.get_fields(cursor=cursor)

        for r in results:

            loc = r['location']
            if loc:
                loc = loc.replace("POINT(", "")
                loc = loc.replace(")", "")
                loc_array = loc.split(" ")
                longitude = loc_array[0]
                latitude = loc_array[1]
            else:
                longitude = None
                latitude = None

            country = {
                'id': r['country_id'],
                'name': r['country_name'],
                'total_projects': r['total_projects'],
                'latitude': latitude,
                'longitude': longitude
            }

            if total_commitments_q:
                country['total_commitment'] = r['total_commitment']
            else:
                country['total_budget'] = r['total_budget']
            activities.append(country)

        return_json = {
            'objects': activities
        }
        cursor = connection.cursor()
        query = 'SELECT c.code ' + ''.join(query_join)
        query += 'WHERE c.code is not null %s GROUP BY c.code' % filter_string

        if include_unesco_empty and organisation_q:
            query = query.replace(organisation_q, "")
            query = query.replace(' AND (' + organisation_q[:-6], "")
            query = query.replace(organisation_q[:-6], "")
            query = query.replace("LEFT JOIN iati_activity a ON rc.activity_id = a.id", "LEFT JOIN iati_activity a ON rc.activity_id = a.id AND " + organisation_q[:-8])
            query = query.replace("WHERE ", "WHERE unesco_region_id is not null AND ")

        cursor.execute(query)
        results2 = helper.get_fields(cursor=cursor)
        return_json["meta"] = {"total_count": len(results2)}

        if output_format == "json":
            return HttpResponse(ujson.dumps(return_json), content_type='application/json')

        if output_format == "xml":

            for item in return_json["objects"]:
                item["name"] = item["name"].encode('utf-8', 'ignore')

            xml = dict2xml(return_json, "objects", True, "country")
            return HttpResponse(xml, content_type='application/xml')

        if output_format == "csv":
            csvh = CsvHelper()
            csv_content = csvh.to_csv(return_json)
            return HttpResponse(csv_content, content_type='text/csv')


class RegionActivitiesResource(ModelResource):

    class Meta:
        #aid_type is used as dummy
        queryset = AidType.objects.none()
        resource_name = 'region-activities'
        include_resource_uri = True
        cache = NoTransformCache()
        serializer = CsvHelper()
        allowed_methods = ['get']


    def get_list(self, request, **kwargs):

        validator = Validator()
        cururl = request.META['PATH_INFO'] + "?" + request.META['QUERY_STRING']
        if not 'flush' in cururl and validator.is_cached(cururl):
            return HttpResponse(validator.get_cached_call(cururl), content_type='application/json')

        helper = CustomCallHelper()
        budget_q_gte = request.GET.get('total_budget__gt', None)
        budget_q_lte = request.GET.get('total_budget__lt', None)
        region_q = helper.get_and_query(request, 'regions__in', 'r.code')
        sector_q = helper.get_and_query(request, 'sectors__in', 's.sector_id')
        organisation_q = helper.get_and_query(request, 'reporting_organisation__in', 'a.reporting_organisation_id')
        budget_q = ''
        limit = request.GET.get("limit", 999)
        offset = request.GET.get("offset", 0)
        order_by = request.GET.get("order_by", "region_name")
        order_asc_desc = request.GET.get("order_asc_desc", "ASC")
        start_actual_q = helper.get_year_and_query(request, 'start_actual__in', 'a.start_actual')
        start_planned_q = helper.get_year_and_query(request, 'start_planned__in', 'a.start_planned')
        vocabulary_q = helper.get_and_query(request, "vocabulary__in", "rv.code")
        region_query = request.GET.get("region", None)
        project_query = request.GET.get("query", None)
        donor_q = helper.get_and_query(request, 'participating_organisations__organisation__code__in', 'apo.organisation_id')
        output_format = request.GET.get("format", "json")
        total_commitments_q = request.GET.get("total_commitments", None)

        if budget_q_gte:
            budget_q += ' a.total_budget > "' + budget_q_gte + '" ) AND ('
        if budget_q_lte:
            budget_q += ' a.total_budget < "' + budget_q_lte + '" ) AND ('

        filter_string = ''.join([
            organisation_q,
            region_q,
            sector_q,
            budget_q,
            start_planned_q,
            start_actual_q,
            vocabulary_q,
            donor_q])

        if filter_string:
            filter_string = ' AND (' + filter_string[:-7] + ') '

        query_select = [
            'SELECT r.code as region_id',
            'r.name as region_name',
            'AsText(r.center_longlat) as location',
        ]

        query_join = [
            'FROM iati_activity a ',
            'LEFT JOIN iati_activityrecipientregion rr ON rr.activity_id = a.id ',
            'LEFT JOIN geodata_region r ON rr.region_id = r.code '
        ]

        if total_commitments_q:
            query_join.append('LEFT JOIN iati_transaction tr ON tr.activity_id = a.id ')
            query_select.append('sum(tr.value) as total_commitment')
            query_select.append('count(distinct(a.id)) as total_projects')
            filter_string += ' AND tr.transaction_type_id = "C" '
        else:
            query_select.append('sum(a.total_budget) as total_budget')
            query_select.append('count(a.id) as total_projects',)

        if sector_q:
            query_join.append('LEFT JOIN iati_activitysector s ON a.id = s.activity_id ')

        if vocabulary_q:
            query_join.append("LEFT JOIN iati_regionvocabulary rv ON r.region_vocabulary_id = rv.code ")

        if region_query:
            filter_string += 'AND r.name LIKE "%%' + region_query + '%%" '

        if project_query:
            query_join.append('LEFT JOIN iati_title as t on a.id = t.activity_id ')
            filter_string += 'AND t.title LIKE "%%' + project_query + '%%" '

        if donor_q:
            query_join.append('LEFT JOIN iati_activityparticipatingorganisation as apo on a.id = apo.activity_id ')
            filter_string += ' AND apo.role_id = "Funding" '

        cursor = connection.cursor()
        cursor.execute(
            ','.join(query_select) + ' ' + ''.join(query_join) +
            'WHERE r.code is not null %s '\
            'GROUP BY r.code ' \
            'ORDER BY %s %s ' \
            'LIMIT %s OFFSET %s' % (filter_string, order_by, order_asc_desc, limit, offset))

        activities = []

        results = helper.get_fields(cursor=cursor)
        for r in results:

            loc = r['location']
            if loc:
                loc = loc.replace("POINT(", "")
                loc = loc.replace(")", "")
                loc_array = loc.split(" ")
                longitude = loc_array[0]
                latitude = loc_array[1]
            else:
                longitude = None
                latitude = None

            region = {
                'id': r['region_id'],
                'name': r['region_name'],
                'total_projects': r['total_projects'],
                'longitude': longitude,
                'latitude': latitude
            }

            if total_commitments_q:
                region['total_commitment'] = r['total_commitment']
            else:
                region['total_budget'] = r['total_budget']

            activities.append(region)

        cursor.execute(','.join(query_select) +
                       ' ' +
                       ''.join(query_join) +
                       'WHERE r.code is not null %s GROUP BY r.code ' % filter_string)
        results2 = helper.get_fields(cursor=cursor)

        return_json = {
            'objects': activities,
            'meta': {"total_count": len(results2)}
        }

        if output_format == "json":
            return HttpResponse(ujson.dumps(return_json), content_type='application/json')

        if output_format == "xml":

            for item in return_json["objects"]:
                item["name"] = item["name"].encode('utf-8', 'ignore')
                item["name"] = item["name"].replace("&", "and")

            xml = dict2xml(return_json, "objects", True, "region")
            return HttpResponse(xml, content_type='application/xml')

        if output_format == "csv":
            csvh = CsvHelper()
            csv_content = csvh.to_csv(return_json)
            return HttpResponse(csv_content, content_type='text/csv')


class GlobalActivitiesResource(ModelResource):

    class Meta:
        queryset = AidType.objects.none()
        resource_name = 'global-activities'
        include_resource_uri = True
        cache = NoTransformCache()
        serializer = CsvHelper()
        allowed_methods = ['get']

    def get_list(self, request, **kwargs):

        helper = CustomCallHelper()
        budget_q_gte = request.GET.get('total_budget__gt', None)
        budget_q_lte = request.GET.get('total_budget__lt', None)
        region_q = helper.get_and_query(request, 'regions__in', 'r.code')
        sector_q = helper.get_and_query(request, 'sectors__in', 's.sector_id')
        organisation_q = helper.get_and_query(request, 'reporting_organisation__in', 'a.reporting_organisation_id')
        budget_q = ''
        start_actual_q = helper.get_year_and_query(request, 'start_actual__in', 'a.start_actual')
        start_planned_q = helper.get_year_and_query(request, 'start_planned__in', 'a.start_planned')
        vocabulary_q = helper.get_and_query(request, "vocabulary__in", "rv.code")
        project_query = request.GET.get("query", None)
        donor_q = helper.get_and_query(request, 'participating_organisations__organisation__code__in', 'apo.organisation_id')
        total_commitments_q = request.GET.get("total_commitments", None)

        if budget_q_gte:
            budget_q += ' a.total_budget > "' + budget_q_gte + '" ) AND ('
        if budget_q_lte:
            budget_q += ' a.total_budget < "' + budget_q_lte + '" ) AND ('

        filter_string = ''.join([
            organisation_q,
            region_q,
            sector_q,
            budget_q,
            start_planned_q,
            start_actual_q,
            vocabulary_q,
            donor_q])

        if filter_string:
            filter_string = ' AND (' + filter_string[:-7] + ') '

        query_select = [
            'SELECT count(a.id) as total_projects',
        ]

        query_join = [
            'FROM iati_activity a '
        ]

        if total_commitments_q:
            query_join.append('LEFT JOIN iati_transaction tr ON tr.activity_id = a.id ')
            query_select.append('sum(tr.value) as total_commitment')
            query_select.append('count(distinct(a.id)) as total_projects')
            filter_string += ' AND tr.transaction_type_id = "C" '
        else:
            query_select.append('sum(a.total_budget) as total_budget')
            query_select.append('count(a.id) as total_projects',)

        if sector_q:
            query_join.append('LEFT JOIN iati_activitysector s ON a.id = s.activity_id ')

        if vocabulary_q:
            query_join.append('LEFT JOIN iati_regionvocabulary rv ON r.region_vocabulary_id = rv.code ')

        if region_q:
            query_join.append(
                'LEFT JOIN iati_activityrecipientregion rr ON rr.activity_id = a.id '
                'LEFT JOIN geodata_region r ON rr.region_id = r.code ')

        if project_query:
            query_join.append('LEFT JOIN iati_title as t on a.id = t.activity_id ')
            filter_string += 'AND t.title LIKE "%%' + project_query + '%%" '

        if donor_q:
            query_join.append('LEFT JOIN iati_activityparticipatingorganisation as apo on a.id = apo.activity_id ')
            filter_string += ' AND apo.role_id = "Funding" '

        cursor = connection.cursor()
        cursor.execute(
            ','.join(query_select) +
            ' ' +
            ''.join(query_join) +
            'WHERE a.scope_id = 1 %s GROUP BY a.scope_id ' % filter_string)
        activities = []

        results = helper.get_fields(cursor=cursor)
        for r in results:
            global_activities = {
                'total_projects': r['total_projects'],
            }
            if total_commitments_q:
                global_activities['total_commitment'] = r['total_commitment']
            else:
                global_activities['total_budget'] = r['total_budget']
            activities.append(global_activities)

        return_json = {
            'objects': activities,
            'meta': {'total_count': 1}
        }

        return HttpResponse(ujson.dumps(return_json), content_type='application/json')


class SectorActivitiesResource(ModelResource):

    class Meta:
        queryset = AidType.objects.none()
        resource_name = 'sector-activities'
        include_resource_uri = True
        cache = NoTransformCache()
        serializer = CsvHelper()
        allowed_methods = ['get']

    def get_list(self, request, **kwargs):

        helper = CustomCallHelper()
        country_q = helper.get_and_query(request, 'countries__in', 'c.code')
        budget_q_gte = request.GET.get('total_budget__gt', None)
        budget_q_lte = request.GET.get('total_budget__lt', None)
        region_q = helper.get_and_query(request, 'regions__in', 'r.code')
        sector_q = helper.get_and_query(request, 'sectors__in', 's.code')
        organisation_q = helper.get_and_query(request, 'reporting_organisation__in', 'a.reporting_organisation_id')
        budget_q = ''
        limit = request.GET.get("limit", 999)
        offset = request.GET.get("offset", 0)
        order_by = request.GET.get("order_by", "sector_name")
        order_asc_desc = request.GET.get("order_asc_desc", "ASC")
        search_query = request.GET.get("query", None)
        output_format = request.GET.get("format", "json")
        total_commitments_q = request.GET.get("total_commitments", None)

        if budget_q_gte:
            budget_q += ' a.total_budget > "' + budget_q_gte + '" ) AND ('
        if budget_q_lte:
            budget_q += ' a.total_budget < "' + budget_q_lte + '" ) AND ('

        filter_string = ''.join([
            country_q,
            organisation_q,
            region_q,
            sector_q,
            budget_q
        ])
        if filter_string:
            filter_string = ' AND (' + filter_string[:-7] + ') '

        query_select = [
            'SELECT s.code as sector_id',
            's.name as sector_name',
        ]

        query_join = [
            'FROM iati_activity a ',
            'LEFT JOIN iati_activitysector acts ON acts.activity_id = a.id '
            'LEFT JOIN iati_sector s ON s.code = acts.sector_id '
        ]

        if total_commitments_q:
            query_join.append('LEFT JOIN iati_transaction tr ON tr.activity_id = a.id ')
            query_select.append('sum(tr.value) as total_commitment')
            query_select.append('count(distinct(a.id)) as total_projects')
            filter_string += ' AND tr.transaction_type_id = "C" '
        else:
            query_select.append('sum(a.total_budget) as total_budget')
            query_select.append('count(a.id) as total_projects',)


        if country_q:
            query_join.append(
                'LEFT JOIN iati_activityrecipientcountry rc ON rc.activity_id = a.id '
                'LEFT JOIN geodata_country c ON rc.region_id = c.code ')

        if region_q:
            query_join.append(
                'LEFT JOIN iati_activityrecipientregion rr ON rr.activity_id = a.id '
                'LEFT JOIN geodata_region r ON rr.region_id = r.code ')

        if search_query:
            filter_string += 'AND s.name LIKE "%%' + search_query + '%%" '

        cursor = connection.cursor()
        cursor.execute(
            ','.join(query_select) + ' ' + ''.join(query_join) +
            'WHERE s.code is not null %s'\
            'GROUP BY s.code ' \
            'ORDER BY %s %s ' \
            'LIMIT %s OFFSET %s' % (filter_string, order_by, order_asc_desc, limit, offset))

        activities = []

        results = helper.get_fields(cursor=cursor)
        for r in results:
            sector = {
                'id': r['sector_id'],
                'name': r['sector_name'],
                'total_projects': r['total_projects']
            }
            if total_commitments_q:
                sector['total_commitment'] = r['total_commitment']
            else:
                sector['total_budget'] = r['total_budget']

            activities.append(sector)

        cursor.execute(','.join(query_select) + ' ' + ''.join(query_join) +
                       'WHERE s.code is not null %s GROUP BY s.code ' % filter_string)

        results2 = helper.get_fields(cursor=cursor)

        return_json = {
            'objects': activities,
            'meta': {'total_count': len(results2)}
        }

        if output_format == "json":
            return HttpResponse(ujson.dumps(return_json), content_type='application/json')

        if output_format == "xml":

            for item in return_json["objects"]:
                item["name"] = item["name"].encode('utf-8', 'ignore')
                item["name"] = item["name"].replace("&", "and")

            xml = dict2xml(return_json, "objects", True, "sector")
            return HttpResponse(xml, content_type='application/xml')

        if output_format == "csv":
            csvh = CsvHelper()
            csv_content = csvh.to_csv(return_json)
            return HttpResponse(csv_content, content_type='text/csv')


class DonorActivitiesResource(ModelResource):

    class Meta:
        queryset = AidType.objects.none()
        resource_name = 'donor-activities'
        include_resource_uri = True
        cache = NoTransformCache()
        allowed_methods = ['get']
        serializer = CsvHelper()

    def get_list(self, request, **kwargs):

        helper = CustomCallHelper()
        country_q = helper.get_and_query(request, 'countries__in', 'c.code')
        budget_q_gte = request.GET.get('total_budget__gt', None)
        budget_q_lte = request.GET.get('total_budget__lt', None)
        region_q = helper.get_and_query(request, 'regions__in', 'r.code')
        sector_q = helper.get_and_query(request, 'sectors__in', 's.sector_id')
        donor_q = helper.get_and_query(request, 'donors__in', 'apo.organisation_id')
        organisation_q = helper.get_and_query(request, 'reporting_organisation__in', 'a.reporting_organisation_id')
        start_actual_q = helper.get_year_and_query(request, 'start_actual__in', 'a.start_actual')
        start_planned_q = helper.get_year_and_query(request, 'start_planned__in', 'a.start_planned')
        budget_q = ''
        limit = request.GET.get("limit", 999)
        offset = request.GET.get("offset", 0)
        order_by = request.GET.get("order_by", "apo.name")
        order_asc_desc = request.GET.get("order_asc_desc", "ASC")
        donor_query = request.GET.get("donor", None)
        project_query = request.GET.get("query", None)
        output_format = request.GET.get("format", "json")
        total_commitments_q = request.GET.get("total_commitments", None)

        if budget_q_gte:
            budget_q += ' a.total_budget > "' + budget_q_gte + '" ) AND ('
        if budget_q_lte:
            budget_q += ' a.total_budget < "' + budget_q_lte + '" ) AND ('

        filter_string = ''.join([
            country_q,
            organisation_q,
            region_q,
            sector_q,
            budget_q,
            start_planned_q,
            start_actual_q,
            donor_q
        ])

        if filter_string:
            filter_string = ' AND (' + filter_string[:-7] + ') '

        query_select = [
            'SELECT apo.organisation_id as organisation_id',
            'apo.name as organisation_name',
            'count(a.id) as total_projects',
            'sum(a.total_budget) as total_budget'
        ]

        query_join = [
            'FROM iati_activity a ',
            'LEFT JOIN iati_activityparticipatingorganisation as apo on a.id = apo.activity_id ',
        ]

        if total_commitments_q:
            query_join.append('LEFT JOIN iati_transaction tr ON tr.activity_id = a.id ')
            query_select.append('sum(tr.value) as total_commitment')
            query_select.append('count(distinct(a.id)) as total_projects')
            filter_string += ' AND tr.transaction_type_id = "C" '
        else:
            query_select.append('sum(a.total_budget) as total_budget')
            query_select.append('count(a.id) as total_projects',)

        if region_q:
            query_join.append(
                'LEFT JOIN iati_activityrecipientregion rr ON rr.activity_id = a.id '
                'LEFT JOIN geodata_region r ON rr.region_id = r.code ')

        if sector_q:
            query_join.append('LEFT JOIN iati_activitysector s ON a.id = s.activity_id ')

        if country_q:
            query_join.append(
                'LEFT JOIN iati_activityrecipientcountry as rc on rc.activity_id = a.id '
                'LEFT JOIN geodata_country c on rc.country_id = c.code ')
            filter_string += ' AND apo.role_id = "Funding" '

        filter_string += ' AND apo.role_id = "Funding" '

        if donor_query:
            filter_string += 'AND apo.name LIKE "%%' + donor_query + '%%" '

        if project_query:
            query_join.append('LEFT JOIN iati_title as t on a.id = t.activity_id ')
            filter_string += 'AND t.title LIKE "%%' + project_query + '%%" '

        cursor = connection.cursor()
        cursor.execute(
            ','.join(query_select) + ' ' + ''.join(query_join) +
            'WHERE apo.name is not null %s'
            'GROUP BY apo.name '
            'ORDER BY %s %s '
            'LIMIT %s OFFSET %s'
            % (
                filter_string,
                order_by,
                order_asc_desc,
                limit,
                offset))

        activities = []

        results = helper.get_fields(cursor=cursor)
        for r in results:
            donor = {
                'id': r['organisation_id'],
                'name': r['organisation_name'],
                'total_projects': r['total_projects'],
            }

            if total_commitments_q:
                donor['total_commitment'] = r['total_commitment']
            else:
                donor['total_budget'] = r['total_budget']

            activities.append(donor)

        cursor.execute(
            ','.join(query_select) + ' ' + ''.join(query_join) +
            'WHERE apo.name is not null %s'
            'GROUP BY apo.name '
            % filter_string
        )
        results2 = helper.get_fields(cursor=cursor)

        return_json = {
            'objects': activities,
            'meta': {"total_count": len(results2)}
        }

        if output_format == "json":
            return HttpResponse(ujson.dumps(return_json), content_type='application/json')

        if output_format == "xml":

            for item in return_json["objects"]:
                item["name"] = item["name"].encode('utf-8', 'ignore')
                item["name"] = item["name"].replace("&", "and")

            xml = dict2xml(return_json, "objects", True, "donor")
            return HttpResponse(xml, content_type='application/xml')

        if output_format == "csv":
            csvh = CsvHelper()
            csv_content = csvh.to_csv(return_json)
            return HttpResponse(csv_content, content_type='text/csv')


class ActivityListVisResource(ModelResource):

    class Meta:
        resource_name = 'activity-list-vis'
        allowed_methods = ['get']


    def get_list(self, request, **kwargs):

        helper = CustomCallHelper()
        cursor = connection.cursor()
        organisations = request.GET.get("reporting_organisation__in", None)
        country_q = helper.get_and_query(request, 'countries__in', 'c.code')
        region_q = helper.get_and_query(request, 'regions__in', 'r.code')
        sector_q = helper.get_and_query(request, 'sectors__in', 's.sector_id')
        budget_q_gte = request.GET.get('total_budget__gt', None)
        budget_q_lte = request.GET.get('total_budget__lt', None)
        query = request.GET.get("query", None)

        budget_q = ''
        if budget_q_gte:
            budget_q += ' a.total_budget > "' + budget_q_gte + '" ) AND ('
        if budget_q_lte:
            budget_q += ' a.total_budget < "' + budget_q_lte + '" ) AND ('

        if organisations:
            q_organisations = 'AND a.reporting_organisation_id = "' + organisations + '"'
        else:
            q_organisations = ""

        filter_string = ' AND (' + country_q + region_q + sector_q + budget_q + ')'
        if 'AND ()' in filter_string:
            filter_string = filter_string[:-6]

        filter_country = ''
        if country_q:
            filter_country = 'LEFT JOIN iati_activityrecipientcountry as rc on rc.activity_id = a.id LEFT JOIN geodata_country c on rc.country_id = c.code '

        filter_sector = ''
        if sector_q:
            filter_sector = 'LEFT JOIN iati_activitysector s ON a.id = s.activity_id '

        if query:
            filter_string += 'AND t.title LIKE "%%' + query + '%%" '

        cursor.execute('SELECT a.id, r.code, r.name, t.title, a.total_budget '
        'FROM iati_activity as a '
        'JOIN iati_activityrecipientregion as rr on a.id = rr.activity_id '
        'JOIN geodata_region as r on r.code = rr.region_id '
        'JOIN iati_title as t on a.id = t.activity_id '
        '%s %s '
        'WHERE 1 %s %s '
        'order by a.id LIMIT 5000' % (filter_country, filter_sector, q_organisations, filter_string))
        results1 = helper.get_fields(cursor=cursor)

        activities = []

        for r in results1:
            activities.append(r)

        return HttpResponse(ujson.dumps(activities), content_type='application/json')



class  PoliciyMarkerSectorResource(ModelResource):
  class Meta:
        resource_name = 'policy-marker-sector-list-vis'
        allowed_methods = ['get']


  def get_list(self, request, **kwargs):

    helper = CustomCallHelper()
    cursor = connection.cursor()
    policy_marker = request.GET.get("policy_marker", "Gender Equality")
    year = request.GET.get("year", "2015")
    publisher_org = request.GET.get("publisher_org", "NL-1")
    query = """SELECT  
        pm.name AS policy_marker,sector_cat.name AS sector,sector_cat.code AS code, ps.name as significance,SUM(a.total_budget) AS total_budget ,SUM(trans.value) AS total_disbursement
      FROM 
        iati_activity AS a 
        INNER JOIN 
        iati_activitypolicymarker AS apm ON (a.id = apm.activity_id)
        INNER JOIN 
        iati_policymarker AS pm ON (pm.code = apm.policy_marker_id)
        INNER JOIN 
        iati_policysignificance AS ps ON (apm.policy_significance_id = ps.code) 
        INNER JOIN 
        iati_activitysector AS actsector ON (a.id = actsector.activity_id)
        INNER JOIN 
        iati_sector AS sector  ON (actsector.sector_id = sector.code)
        INNER JOIN 
        iati_sectorcategory AS sector_cat ON (sector.category_id = sector_cat.code )
        INNER JOIN
        iati_transaction AS trans ON (a.id = trans.activity_id)
        INNER JOIN 
        iati_transactiontype AS trans_type ON (trans.transaction_type_id = trans_type.code)
        INNER JOIN 
        iati_organisation AS reporting_org ON (a.reporting_organisation_id = reporting_org.id)
      WHERE 
        trans_type.name = 'Disbursement' AND
        YEAR(trans.transaction_date) =  {year} AND
        reporting_org.code = '{publisher_org}'  AND
        pm.name = '{policy_marker}'
        
      GROUP BY pm.code,sector_cat.name,sector_cat.code,ps.code
      ORDER BY pm.code,sector_cat.name,sector_cat.code,ps.code"""
    query = query.format(policy_marker=policy_marker, year=year, publisher_org=publisher_org)
    cursor.execute(query)
    results1 = helper.get_fields(cursor=cursor)

    sectors = []
    old_sector = ''
    current_sector = {}
    

    for r in results1:
      if r['sector'] != old_sector:
        if old_sector != '':
          sectors.append(current_sector)
        old_sector = r['sector']
        current_sector = {}
        current_sector['name'] = r['sector']
        current_sector['categrory_code'] = r['code']
        current_sector['significance'] = {}
      current_sector['significance'][r['significance']] = r['total_disbursement']


    return HttpResponse(ujson.dumps(sectors), content_type='application/json')
