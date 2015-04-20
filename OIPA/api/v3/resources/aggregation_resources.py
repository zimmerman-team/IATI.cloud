# Tastypie specific
from tastypie.resources import ModelResource

# cache specific
from api.cache import NoTransformCache
from iati.models import AidType
from iati.models import Activity
from cache.validator import Validator

# Direct sql specific
import ujson
from django.db import connection
from django.http import HttpResponse

# Helpers
from api.v3.resources.custom_call_helper import CustomCallHelper

class ActivityAggregatedAnyResource(ModelResource):

    class Meta:
        queryset = Activity.objects.none()
        resource_name = 'activity-aggregate-any'
        include_resource_uri = True
        cache = NoTransformCache()
        allowed_methods = ['get']


    def get_list(self, request, **kwargs):

        # get group by and aggregation pars
        group_by_key = request.GET.get('group_by', None)
        aggregation_key = request.GET.get('aggregation_key', 'iati-identifier')
        group_field = request.GET.get('group_field', 'start_actual')
        group_by_arr = [];
        if ',' in group_by_key:
            group_by_arr = group_by_key.split(',')
        else:
            group_by_arr.append(group_by_key)
        group_by_key = group_by_arr[0]

        query = request.GET.get('query', '')

        if group_by_key in {'commitment', 'disbursement', 'incoming-fund'}:
            group_field = 't.value_date'

        aggregation_element_dict = {
            'iati-identifier': {
                'select': 'a.id',
                'type': 'count',
                'from_addition': ''},
            'reporting-org': {
                'select': 'a.reporting_organisation_id',
                'type': 'count',
                'from_addition': ''},
            'title': {
                'select': 't.title',
                'type': 'count',
                'from_addition': 'JOIN iati_title as t on a.id = t.activity_id '},
            'description': {
                'select': 'd.description',
                'type': 'count',
                'from_addition': 'JOIN iati_description as d on a.id = d.activity_id '},
            'commitment': {
                'select': 't.value',
                'type': 'sum',
                'from_addition': 'JOIN iati_transaction as t on a.id = t.activity_id ',
                'where_addition': 'AND t.transaction_type_id = "C" '},
            'disbursement': {
                'select': 't.value',
                'type': 'sum',
                'from_addition': 'JOIN iati_transaction as t on a.id = t.activity_id ',
                'where_addition': 'AND t.transaction_type_id = "D" '},
            'expenditure': {
                'select': 't.value',
                'type': 'sum',
                'from_addition': 'JOIN iati_transaction as t on a.id = t.activity_id ',
                'where_addition': 'AND t.transaction_type_id = "E" '},
            'incoming-fund': {
                'select': 't.value',
                'type': 'sum',
                'from_addition': 'JOIN iati_transaction as t on a.id = t.activity_id ',
                'where_addition': 'AND t.transaction_type_id = "IF" '},
            'location': {
                'select': 'l.activity_id',
                'type': 'count',
                'from_addition': 'JOIN iati_location as l on a.id = l.activity_id '},
            'policy-marker': {
                'select': 'pm.policy_marker_id',
                'type': 'count',
                'from_addition': 'JOIN iati_activitypolicymarker as pm on a.id = pm.activity_id '},
            'total-budget': {
                'select': 'a.total_budget',
                'type': 'sum',
                'from_addition': ''},
        }

        group_by_element_dict = {
            'recipient-country': {
                'select': 'rc.country_id',
                'from_addition': 'JOIN iati_activityrecipientcountry as rc on a.id = rc.activity_id '},
            'recipient-country-name':{
                'select': 'country.name',
                'from_addition': 'JOIN geodata_country as country on rc.country_id = country.code '},
            'recipient-region': {
                'select': 'r.name, rr.region_id',
                'from_addition': 'JOIN iati_activityrecipientregion as rr on a.id = rr.activity_id '
                                'join geodata_region as r on rr.region_id = r.code '},
            'year': {
                'select': 'YEAR('+group_field+')',
                'from_addition': ''},
            'sector': {
                'select': 'acts.sector_id',
                'from_addition': 'JOIN iati_activitysector as acts on a.id = acts.activity_id '},
            'reporting-org': {
                'select': 'a.reporting_organisation_id',
                'from_addition': ''},
            'participating-org': {
                'select': 'po.name',
                'from_addition': 'JOIN iati_activityparticipatingorganisation as po on a.id = po.activity_id '},
            'policy-marker': {
                'select': 'pm.policy_marker_id',
                'from_addition': 'JOIN iati_activitypolicymarker as pm on a.id = pm.activity_id '},
            'r.title': {
                'select': 'r.title',
                'from_addition': 'JOIN iati_result as r on a.id = r.activity_id ',
                'where_addition': ' AND r.title = %(query)s '},
            'transaction_date_year':{
                'select': 'year(t.transaction_date) ',
                'from_addition': '',
                'where_addition': ''},
            
        }

        helper = CustomCallHelper()
        cursor = connection.cursor()

        # get filters
        reporting_organisations = helper.get_and_query(
            request,
            'reporting_organisation__in',
            'a.reporting_organisation_id')
        recipient_countries = helper.get_and_query(request, 'countries__in', 'rc.country_id')
        recipient_regions = helper.get_and_query(request, 'regions__in', 'rr.region_id')
        total_budgets = helper.get_and_query(request, 'total_budget__in', 'a.total_budget')
        sectors = helper.get_and_query(request, 'sectors__in', 'acts.sector_id')

        if aggregation_key in aggregation_element_dict:
            aggregation_info = aggregation_element_dict[aggregation_key]
            aggregation_key = aggregation_info["select"]
            aggregation_type = aggregation_info["type"]
            aggregation_from_addition = aggregation_info["from_addition"]
            aggregation_where_addition = ""
            if "where_addition" in aggregation_info:
                aggregation_where_addition = aggregation_info["where_addition"]
        else:
            return HttpResponse(ujson.dumps({
                "error": "Invalid aggregation key, see included list for viable keys.",
                "valid_aggregation_keys": list(aggregation_element_dict.keys())}),
                content_type='application/json')
        
        group_select= [];
        group_from_addition = [];
        for group_by_key in group_by_arr:
            if group_by_key in group_by_element_dict:
                group_by_info = group_by_element_dict[group_by_key]
                group_select.append(group_by_info["select"])
                group_from_addition.append(group_by_info["from_addition"])
                if "where_addition" in group_by_info and query:
                    aggregation_where_addition = aggregation_where_addition.join(group_by_info["where_addition"])
            else:
                return HttpResponse(ujson.dumps({
                    "error": "Invalid group by key, see included list for viable keys.",
                    "valid_group_by_keys": list(group_by_element_dict.keys())}),
                    content_type='application/json')

        # make sure group key and aggregation key are set
        if not group_by_key:
            return HttpResponse(ujson.dumps(
                "No field to group by. add parameter group_by (country/region/etc.. see docs)"),
                content_type='application/json')

        if not aggregation_key:
            return HttpResponse(ujson.dumps(
                "No field to aggregate on. add parameter aggregation_key "),
                content_type='application/json')

        group_select_str_arr = [];
        i = 0;
        index = '';
        for group_select_part in group_select:
            if i != 0:
                index = str(i);
            group_select_str_arr.append(group_select_part+' as group_field'+index+' ')
            i = i+1
        group_select_str = ','.join(group_select_str_arr);
        query_select = ''.join([
            'SELECT ',
            aggregation_type,
            '(',
            aggregation_key,
            ') as aggregation_field, ',
            group_select_str])

        query_from = ''.join([
            'FROM iati_activity as a ',
            aggregation_from_addition,
            ' '.join(group_from_addition)])

        query_where = ''.join([
            'WHERE 1 ',
            aggregation_where_addition])

        query_group_by = ''.join([
            'GROUP BY ',
            ','.join(group_select)])

        # fill where part
        filter_string = ''.join([
            'AND (',
            reporting_organisations,
            recipient_countries,
            recipient_regions,
            total_budgets,
            sectors,
            ')'])

        if filter_string == 'AND ()':
            filter_string = ""
        elif 'AND ()' in filter_string:
            filter_string = filter_string[:-6]

        query_where += filter_string

        if not filter_string and query_from == 'FROM iati_activity as a ':
            if group_by_key == "country":
                query_select = 'SELECT count(activity_id) as aggregation_field, country_id as group_field '
                query_from = "FROM iati_activityrecipientcountry "
                query_group_by = "GROUP BY country_id"

            elif group_by_key == "region":
                query_select = 'SELECT count(activity_id) as aggregation_field, region_id as group_field '
                query_from = "FROM iati_activityrecipientregion "
                query_group_by = "GROUP BY region_id"

            elif group_by_key == "sector":
                query_select = 'SELECT count(activity_id) as aggregation_field, sector_id as group_field '
                query_from = "FROM iati_activitysector "
                query_group_by = "GROUP BY sector_id"

        print query_select + query_from + query_where + query_group_by, {"query": query, }
        cursor.execute(query_select + query_from + query_where + query_group_by, {"query": query, })
        results1 = helper.get_fields(cursor=cursor)

        options = []
        for r in results1:
            options.append(r)

        return HttpResponse(ujson.dumps(options), content_type='application/json')













class ActivityAggregatedAnyNamesResource(ModelResource):

    class Meta:
        #aid_type is used as dummy
        queryset = AidType.objects.all()
        resource_name = 'activity-aggregate-any-names'
        include_resource_uri = True
        cache = NoTransformCache()
        allowed_methods = ['get']


    def get_list(self, request, **kwargs):


        # get group by and aggregation pars
        group_by_key = request.GET.get("group_by", None) # valid : country, region, year, sector, reporting org
        aggregation_key = request.GET.get("aggregation_key", "iati-identifier")
        group_field = request.GET.get("group_field", "start_actual") # used for year filtering, valid : start_planned, start_actual, end_planned, end_actual, defaults to start_actual
        if group_by_key in {'commitment', 'disbursement', 'incoming-fund'}:
            group_field = "t.value_date"

        aggregation_element_dict = {
            'iati-identifier': {'select': 'a.id', 'type': 'count', 'from_addition': ''},
            'reporting-org': {'select': 'a.reporting_organisation_id', 'type': 'count', 'from_addition': ''},
            'title': {'select': 't.title', 'type': 'count', 'from_addition': 'JOIN iati_title as t on a.id = t.activity_id '},
            'description': {'select': 'd.description', 'type': 'count', 'from_addition':'JOIN iati_description as d on a.id = d.activity_id '},
            'commitment': {'select': 't.value', 'type': 'sum', 'from_addition': 'JOIN iati_transaction as t on a.id = t.activity_id ', 'where_addition': 'AND t.transaction_type_id = "C" '},
            'disbursement': {'select': 't.value', 'type': 'sum', 'from_addition': 'JOIN iati_transaction as t on a.id = t.activity_id ', 'where_addition': 'AND t.transaction_type_id = "D" '},
            'incoming-fund': {'select': 't.value', 'type': 'sum', 'from_addition': 'JOIN iati_transaction as t on a.id = t.activity_id ', 'where_addition': 'AND t.transaction_type_id = "IF" '},
            'location': {'select': 'l.activity_id', 'type': 'count', 'from_addition': 'JOIN iati_location as l on a.id = l.activity_id '},
            'policy-marker': {'select': 'pm.policy_marker_id', 'type': 'count', 'from_addition': 'JOIN iati_activitypolicymarker as pm on a.id = pm.activity_id '},
            'total-budget': {'select': 'a.total_budget', 'type': 'sum', 'from_addition': ''},
            # 'recipient-country': {'select': 'a.id', 'type': 'count', 'from_addition': ''},
            # 'recipient-region': {'select': 'a.id', 'type': 'count', 'from_addition': ''},
            # 'year': {'select': 'a.id', 'type': 'count', 'from_addition': ''},
            # 'sector': {'select': 'a.id', 'type': 'count', 'from_addition': ''},
        }

        group_by_element_dict = {
            'recipient-country': {'select': 'rc.country_id', 'from_addition': 'JOIN iati_activityrecipientcountry as rc on a.id = rc.activity_id '},
            'recipient-region': {'select': 'rr.region_id', 'from_addition': 'JOIN iati_activityrecipientregion as rr on a.id = rr.activity_id '},
            'year': {'select': 'YEAR('+group_field+')', 'from_addition': ''},
            'sector': {'select': 'acts.sector_id', 'from_addition': 'JOIN iati_activitysector as acts on a.id = acts.activity_id '},
            'reporting-org': {'select': 'a.reporting_organisation_id', 'from_addition': 'JOIN iati_organisation as o on a.reporting_organisation_id = o.code '},
            'participating-org': {'select': 'po.name', 'from_addition': 'JOIN iati_activityparticipatingorganisation as po on a.id = po.activity_id '},
            'policy-marker': {'select': 'pm.policy_marker_id', 'from_addition': 'JOIN iati_activitypolicymarker as pm on a.id = pm.activity_id '},
        }

        # check if call is cached using validator.is_cached
        # check if call contains flush, if it does the call comes from the cache updater and shouldn't return cached results
        validator = Validator()
        cururl = request.META['PATH_INFO'] + "?" + request.META['QUERY_STRING']

        if not 'flush' in cururl and validator.is_cached(cururl):
            return HttpResponse(validator.get_cached_call(cururl), content_type='application/json')

        helper = CustomCallHelper()
        cursor = connection.cursor()


        # get filters
        reporting_organisations = helper.get_and_query(request, 'reporting_organisation__in', 'a.reporting_organisation_id')
        recipient_countries = helper.get_and_query(request, 'countries__in', 'rc.country_id')
        recipient_regions = helper.get_and_query(request, 'regions__in', 'rr.region_id')
        total_budgets = helper.get_and_query(request, 'total_budget__in', 'a.total_budget')
        sectors = helper.get_and_query(request, 'sectors__in', 'acts.sector_id')





        if aggregation_key in aggregation_element_dict:
            aggregation_info = aggregation_element_dict[aggregation_key]
            aggregation_key = aggregation_info["select"]
            aggregation_type = aggregation_info["type"]
            aggregation_from_addition = aggregation_info["from_addition"]
            aggregation_where_addition = ""
            if "where_addition" in aggregation_info:
                aggregation_where_addition = aggregation_info["where_addition"]
        else:

            return HttpResponse(ujson.dumps({"error": "Invalid aggregation key, see included list for viable keys.","valid_aggregation_keys": list(aggregation_element_dict.keys())}), content_type='application/json')

        if group_by_key in group_by_element_dict:
            group_by_info = group_by_element_dict[group_by_key]
            group_select = group_by_info["select"]
            group_from_addition = group_by_info["from_addition"]
        else:
            return HttpResponse(ujson.dumps({"error": "Invalid group by key, see included list for viable keys.","valid_group_by_keys": list(group_by_element_dict.keys())}), content_type='application/json')

        # make sure group key and aggregation key are set
        if not group_by_key:
            return HttpResponse(ujson.dumps("No field to group by. add parameter group_by (country/region/etc.. see docs)"), content_type='application/json')
        if not aggregation_key:
            return HttpResponse(ujson.dumps("No field to aggregate on. add parameter aggregation_key (iati-identifier/reporting-org/etc.. see docs)"), content_type='application/json')

        #create the query
        query_select = 'SELECT '+aggregation_type+'(' + aggregation_key + ') as aggregation_field, ' + group_select + ' as group_field, o.name   as org_name '
        query_from = 'FROM iati_activity as a ' + aggregation_from_addition + group_from_addition
        query_where = 'WHERE 1 ' + aggregation_where_addition
        query_group_by = 'GROUP BY ' + group_select

        # fill where part
        filter_string = 'AND (' + reporting_organisations + recipient_countries + recipient_regions + total_budgets + sectors + ')'
        if filter_string == 'AND ()':
            filter_string = ""
        else:
            if 'AND ()' in filter_string:
                filter_string = filter_string[:-6]

        query_where += filter_string

        # optimalisation for simple (all) queries
        if not filter_string and query_from == 'FROM iati_activity as a ':
            if(group_by_key == "country"):
                query_select = 'SELECT count(activity_id) as aggregation_field, country_id as group_field '
                query_from = "FROM iati_activityrecipientcountry "
                query_group_by = "GROUP BY country_id"

            elif(group_by_key == "region"):
                query_select = 'SELECT count(activity_id) as aggregation_field, region_id as group_field '
                query_from = "FROM iati_activityrecipientregion "
                query_group_by = "GROUP BY region_id"

            elif(group_by_key == "sector"):
                query_select = 'SELECT count(activity_id) as aggregation_field, sector_id as group_field '
                query_from = "FROM iati_activitysector "
                query_group_by = "GROUP BY sector_id"

        # execute query


        cursor.execute(query_select + query_from + query_where + query_group_by)
        results1 = helper.get_fields(cursor=cursor)

        # query result -> json output

        options = {}

        for r in results1:

            options[r['group_field']] = [r['aggregation_field'], r['org_name']]



        return HttpResponse(ujson.dumps(options), content_type='application/json')
