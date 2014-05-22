# Tastypie specific
from tastypie.resources import ModelResource

# Data specific
from geodata.data_backup.country_data import countryData

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


class ActivityCountResource(ModelResource):

    class Meta:
        #aid_type is used as dummy
        queryset = AidType.objects.all()
        resource_name = 'activity-count'
        include_resource_uri = True
        cache = NoTransformCache()


    def get_list(self, request, **kwargs):

        # check if call is cached using validator.is_cached
        # check if call contains flush, if it does the call comes from the cache updater and shouldn't return cached results
        validator = Validator()
        cururl = request.META['PATH_INFO'] + "?" + request.META['QUERY_STRING']

        if not 'flush' in cururl and validator.is_cached(cururl):
            return HttpResponse(validator.get_cached_call(cururl), mimetype='application/json')


        helper = CustomCallHelper()
        cursor = connection.cursor()


        # get filters
        reporting_organisations = helper.get_and_query(request, 'reporting_organisation__in', 'a.reporting_organisation_id')
        recipient_countries = helper.get_and_query(request, 'countries__in', 'rc.country_id')
        recipient_regions = helper.get_and_query(request, 'regions__in', 'rr.region_id')
        total_budgets = helper.get_and_query(request, 'total_budget__in', 'a.total_budget')
        sectors = helper.get_and_query(request, 'sectors__in', 'acts.sector_id')

        from_countries = False
        from_regions = False
        from_sectors = False

        if recipient_countries:
            from_countries = True
        if recipient_regions:
            from_regions = True
        if sectors:
            from_sectors = True

        # get group by pars
        group_by = request.GET.get("group_by", None) # valid : country, region, year, sector, reporting org
        field = request.GET.get("group_field", "start_actual") # used for year filtering, valid : start_planned, start_actual, end_planned, end_actual, defaults to start_actual


        if not group_by:
            return HttpResponse(ujson.dumps("No field to group by. add parameter group_by (country/region/etc.. see docs)"), mimetype='application/json')


        #create the query
        query_select = 'SELECT count(a.id) as activity_count, '
        query_from = 'FROM iati_activity as a '
        query_where = 'WHERE 1 '
        query_group_by = 'GROUP BY '

        # fill select and group by
        if(group_by == "country"):
            query_select += 'rc.country_id as group_field '
            query_group_by += 'rc.country_id '
            from_countries = True

        elif(group_by == "region"):
            query_select += 'r.region_id as group_field '
            query_group_by += 'r.region_id '
            from_regions = True

        elif(group_by == "year"):
            query_select += 'YEAR(a.'+field+') as group_field '
            query_group_by += 'YEAR(a.'+field+') '

        elif(group_by == "sector"):
            query_select += 'acts.sector_id as group_field '
            query_group_by += 'acts.sector_id '
            from_sectors = True

        elif(group_by == "reporting_organisation"):
            query_select += 'a.reporting_organisation_id as group_field '
            query_group_by += 'a.reporting_organisation_id '


        # fill from part
        if from_countries:
            query_from += "JOIN iati_activityrecipientcountry as rc on a.id = rc.activity_id "
        if from_regions:
            query_from += "JOIN iati_activityrecipientregion as rr on a.id = rr.activity_id "
        if from_sectors:
            query_from += "JOIN iati_activitysector as acts on a.id = acts.activity_id "

        # fill where part
        filter_string = 'AND (' + reporting_organisations + recipient_countries + recipient_regions + total_budgets + sectors + ')'
        if filter_string == 'AND ()':
            filter_string = ""
        else:
            if 'AND ()' in filter_string:
                filter_string = filter_string[:-6]
        print filter_string




        query_where += filter_string

        # optimalisation for simple (all) queries
        if not filter_string:
            # fill select and group by
            if(group_by == "country"):
                query_select = 'SELECT count(activity_id) as activity_count, country_id as group_field '
                query_from = "FROM iati_activityrecipientcountry "
                query_group_by = "GROUP BY country_id"

            elif(group_by == "region"):
                query_select = 'SELECT count(activity_id) as activity_count, region_id as group_field '
                query_from = "FROM iati_activityrecipientregion "
                query_group_by = "GROUP BY region_id"

            elif(group_by == "sector"):
                query_select = 'SELECT count(activity_id) as activity_count, sector_id as group_field '
                query_from = "FROM iati_activitysector "
                query_group_by = "GROUP BY sector_id"

        # execute query

        print query_select + query_from + query_where + query_group_by

        cursor.execute(query_select + query_from + query_where + query_group_by)
        results1 = helper.get_fields(cursor=cursor)

        # query result -> json output

        options = {}

        for r in results1:

            options[r['group_field']] = r['activity_count']



        return HttpResponse(ujson.dumps(options), mimetype='application/json')

