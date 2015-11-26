from django.db.models import Count
from django.db.models import Sum
from django.db.models import Q
from django.db.models.functions import Coalesce
from django.db import connection

from rest_framework.serializers import BaseSerializer

from geodata.models import Country
from geodata.models import Region
from iati.models import Organisation
from iati.models import Sector
from iati.models import ActivityStatus
from iati.models import PolicyMarker
from iati.models import CollaborationType
from iati.models import FlowType
from iati.models import AidType
from iati.models import FinanceType
from iati.models import TiedStatus

from api.activity.serializers import CodelistSerializer
from api.activity.serializers import ParticipatingOrganisationSerializer
from api.country.serializers import CountrySerializer
from api.region.serializers import RegionSerializer
from api.sector.serializers import SectorSerializer


class ActivityAggregationSerializer(BaseSerializer):

    _aggregations = {
        "count": {
            "field": "count",
            "annotate_name": "count",
            "annotate": Count('id', distinct=True)
        },
        "budget": {
            "field": "budget",
            "annotate_name": "budget",
            "annotate": Sum('budget__value')
        },
        "total_budget": {
            "field": "total_budget",
            "annotate_name": 'total_budget',
            "annotate": Sum('total_budget')
        },
        "disbursement": {
            "field": "disbursement",
            "extra_filter": Q(transaction__transaction_type=3),
            "annotate_name": 'disbursement',
            "annotate": Sum('transaction__value'),
        },
        "expenditure": {
            "field": "expenditure",
            "extra_filter": Q(transaction__transaction_type=4),
            "annotate_name": "expenditure",
            "annotate": Sum('transaction__value')
        },
        "commitment": {
            "field": "commitment",
            "extra_filter": Q(transaction__transaction_type=2),
            "annotate_name": 'commitment',
            "annotate": Sum('transaction__value')
        },
        "incoming_fund": {
            "field": "incoming_fund",
            "extra_filter": Q(transaction__transaction_type=1),
            "annotate_name": 'incoming_fund',
            "annotate": Sum('transaction__value')
        },
        "sector_percentage_weighted_budget": {
            "field": "weighted_budget",
            "annotate_name": 'total_budget_per_percentage',
            "annotate": (Coalesce(Sum('budget__value'), 0) * Coalesce('activitysector__percentage', 100) / 100),
            "no_null_check": True,
            "has_subquery": 'select sector_id as sector, sum(total_budget_per_percentage) as budget from ({}) as "temptab" group by "sector_id" order by "sector_id"'
        },
        "location_disbursement": {
            "field": "weighted_country_value",
            "annotate_name": 'value_by_country',
            "annotate": (Coalesce(Sum('location__value'), 0) * Coalesce('activitysector__percentage', 100) / 100),
            "no_null_check": True,
            "has_subquery": 'select loc_country_id, sum(value_by_country) as total_value, region_id, country_name from ({}) as per_activity group by per_activity.loc_country_id'
        }
    }

    _allowed_groupings = {
        "related_activity": {
            "field": "relatedactivity__ref_activity__id",
            "queryset": None,
            "serializer": None,
            "fields": (),
        },
        "recipient_country": {
            "field": "recipient_country",
            "queryset": Country.objects.all(),
            "serializer": CountrySerializer,
            "fields": ('url', 'code', 'name', 'location'),
        },
        "recipient_region": {
            "field": "recipient_region",
            "queryset": Region.objects.all(),
            "serializer": RegionSerializer,
            "fields": ('url', 'code', 'name', 'location'),
        },
        "sector": {
            "field": "sector",
            "queryset": Sector.objects.all(),
            "serializer": SectorSerializer,
            "fields": ('url', 'code', 'name'),
        },
        "reporting_organisation": {
            "field": "reporting_organisations__ref",
            "queryset": None,
            "serializer": None,
            "fields": (),
        },
        "participating_organisation": {
            "field": "participating_organisation",
            "queryset": Organisation.objects.all(),
            "serializer": ParticipatingOrganisationSerializer,
            "fields": ('url', 'code', 'name'),
        },
        "activity_status": {
            "field": "activity_status",
            "queryset": ActivityStatus.objects.all(),
            "serializer": CodelistSerializer,
            "fields": (), # has default fields
        },
        "policy_marker": {
            "field": "policy_marker",
            "queryset": PolicyMarker.objects.all(),
            "serializer": CodelistSerializer,
            "fields": (), # has default fields
        },
        "collaboration_type": {
            "field": "collaboration_type",
            "queryset": CollaborationType.objects.all(),
            "serializer": CodelistSerializer,
            "fields": (), # has default fields
        },
        "default_flow_type": {
            "field": "default_flow_type",
            "queryset": FlowType.objects.all(),
            "serializer": CodelistSerializer,
            "fields": (), # has default fields
        },
        "default_aid_type": {
            "field": "default_aid_type",
            "queryset": AidType.objects.all(),
            "serializer": CodelistSerializer,
            "fields": (), # has default fields
        },
        "default_finance_type": {
            "field": "default_finance_type",
            "queryset": FinanceType.objects.all(),
            "serializer": CodelistSerializer,
            "fields": (), # has default fields
        },
        "default_tied_status": {
            "field": "default_tied_status",
            "queryset": TiedStatus.objects.all(),
            "serializer": CodelistSerializer,
            "fields": (), # has default fields
        },
        "budget_per_year": {
            "field": "year",
            "extra": { 
                'year': 'EXTRACT(YEAR FROM "period_start")::integer',
            },
            "queryset": None,
            "serializer": None,
            "fields": (),
        },
        "budget_per_quarter": {
            "field": "year,quarter",
            "extra": {
                'year': 'EXTRACT(YEAR FROM "period_start")::integer',
                'quarter': 'EXTRACT(QUARTER FROM "period_start")::integer',
            },
            "queryset": None,
            "serializer": None,
            "fields": (),
        },
        "transaction_date_year": {
            "field": "year",
            "extra": {
                'year': 'EXTRACT(YEAR FROM "transaction_date")::integer',
            },
            "queryset": None,
            "serializer": None,
            "fields": (),
        },
        "transactions_per_quarter": {
            "field": "year,quarter",
            "extra": {
                'year': 'EXTRACT(YEAR FROM "transaction_date")::integer',
                'quarter': 'EXTRACT(QUARTER FROM "transaction_date")::integer',
            },
            "queryset": None,
            "serializer": None,
            "fields": (),
        },
        "location_country": {
            "field": "'a.id, l.adm_country_iso_id as loc_country_id, lc.name as country_name, lc.region_id",
            "queryset": None,
            "serializer": None,
            "fields": (),
        },
    }

    _allowed_orderings = [ i['field'] for i in _allowed_groupings.values()]

    def apply_order_filters(self, queryset, orderList, aggregationList):

        allowed_orderings = self._allowed_orderings + aggregationList
        allowed_orderings = allowed_orderings + ['-' + o for o in allowed_orderings]

        orderings = self._intersection(allowed_orderings, orderList)

        if (len(orderings)):
            return queryset.order_by(*orderings)
        # else: 
        #     return queryset.order_by(*self._intersection(allowed_orderings, groupList))

        return queryset

    def apply_limit_offset_filters(self, queryset, page_size, page):

        if page_size:

            if not page:
                page = 1

            page_size = int(page_size)
            page = int(page)

            offset = (page * page_size) - page_size
            offset_plus_limit = offset + page_size
            return queryset[offset:offset_plus_limit]

        return queryset

    def apply_annotations(self, queryset, groupList, aggregationList):

        first_queryset = queryset
        first_annotations = dict()

        same_query_aggregations = [i for i in aggregationList if not self._aggregations[i].get('extra_filter')]
        separate_aggregations = [i for i in aggregationList if self._aggregations[i].get('extra_filter')]

        for aggregation in same_query_aggregations:
            a = self._aggregations.get(aggregation, {})
            first_annotations[a['annotate_name']] = a['annotate']
     
        # aggregations that can be performed in the same query (hence require no extra filters)
        groupings = {group: self._allowed_groupings[group] for group in groupList}
        groupFields = []
        for grouping in groupings.values():
            groupFields.extend(grouping["field"].split(','))
        groupExtras = {"select": grouping["extra"] for grouping in groupings.values() if "extra" in grouping}

        # apply extras
        first_queryset = first_queryset.extra(**groupExtras)
        queryset = first_queryset.extra(**groupExtras)

        # remove nulls (
        # to do: check why values() uses left outer joins,
        # this can be a lot slower than inner joins and will prevent the null
        nullFilters = {}
        for grouping in groupings.values():
            if grouping["fields"]:
                nullFilters[grouping["field"] + '__isnull'] = False
        for aggregation in same_query_aggregations:
            nullFilters[aggregation + '__isnull'] = False
            if 'no_null_check' in self._aggregations[aggregation]:
                nullFilters = {}

        # Apply group_by calls and annotations
        result = first_queryset.values(*groupFields).annotate(**first_annotations).filter(**nullFilters)

        # aggregations that require extra filters, and hence must be executed separately
        for aggregation in separate_aggregations:

            a = self._aggregations.get(aggregation, None)
            extra_filter = a["extra_filter"]
            field = a["field"]
            annotation = dict([(a['annotate_name'], a['annotate'])])

            if len(same_query_aggregations) is 0:
                result = queryset.filter(extra_filter).values(*groupFields).annotate(**annotation)
                continue

            next_result = queryset.filter(extra_filter).values(*groupFields).annotate(**annotation)

            print str(next_result.query)
            main_group_field = groupFields[0]

            if len(next_result):
                # join results in results object (first_result >= new_result)
                iold = iter(result)
                inew = iter(next_result)

                n = next(inew)
                for o in iold: 

                    if (n[main_group_field] == o[main_group_field]):
                        o[field] = n[field]

                        try:
                            n = next(inew)
                        except StopIteration:
                            break

        return result

    def apply_extra_calculations(self, results, aggregations):

        # check if subquery required
        subquery_aggregations = [self._aggregations[i] for i in aggregations if self._aggregations[i].get('has_subquery')]

        if len(subquery_aggregations):

            sql, params = results.query.sql_with_params()
            cursor = connection.cursor()
            cursor.execute(
                subquery_aggregations[0]['has_subquery'].format(sql),
                params)

            def dictfetchall(cursor):
                columns = [col[0] for col in cursor.description]
                return [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                ]

            results = dictfetchall(cursor)

        return list(results)

    def serialize_foreign_keys(self, results, request, groupList):

        serializers = {}

        for grouping in groupList:
            serializer = self._allowed_groupings[grouping]["serializer"]
            fields = self._allowed_groupings[grouping]["fields"]
            foreignQueryset = self._allowed_groupings[grouping]["queryset"]

            if serializer:
                data = serializer(foreignQueryset,
                    context={
                        'request': request,
                    },
                    many=True,
                    fields=fields,
                ).data

                serializers[grouping] = {i.get('code'): i for i in data}

            else:
                serializers[grouping] = {i.get(grouping): i.get(grouping) for i in results}

        for i, result in enumerate(list(results)):
            for k, v in result.iteritems():
                if k in groupList:
                    if v:
                        result[k] = serializers.get(k, {}).get(str(v))
                    else:
                        del results[i]

        return results

    def to_representation(self, queryset):
        request = self.context.get('request') 
        params = request.query_params

        order_by = filter(None, params.get('order_by', "").split(','))
        page_size = params.get('page_size', None)
        page = params.get('page', None)

        group_by = self._intersection(filter(None, params.get('group_by', "").split(',')), self._allowed_groupings.keys())
        aggregations = self._intersection(filter(None,params.get('aggregations', "").split(',')), self._aggregations.keys())

        if not len(group_by):
            return {'error_message': "Invalid value for mandatory field 'group_by'"}
        elif not len(aggregations):
            return {'error_message': "Invalid value for mandatory field 'aggregations'"}

        # queryset = self.apply_group_filters(queryset, request, group_by)
        queryset = self.apply_order_filters(queryset, order_by, aggregations)
        queryset = self.apply_annotations(queryset, group_by, aggregations)
        result = self.apply_limit_offset_filters(queryset, page_size, page)
        result = self.apply_extra_calculations(result, aggregations)
        result = self.serialize_foreign_keys(result, request, group_by)

        return {
            'count':len(queryset),
            'results': result
        }

    def _union(self, list1, list2):
        return list(set(list1) | set(list2))

    def _intersection(self, list1, list2):
        return list(set(list1) & set(list2))
