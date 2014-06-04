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