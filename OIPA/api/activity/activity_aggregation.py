from django.db.models import Count
from django.db.models import Sum
from django.db.models import Q, F
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
from iati.models import DocumentCategory
from iati.models import FlowType
from iati.models import AidType
from iati.models import FinanceType
from iati.models import TiedStatus
from iati.models import ActivityParticipatingOrganisation
from iati.models import ActivityReportingOrganisation

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
            "fields": "relatedactivity__ref_activity__id",
            "queryset": None,
            "serializer": None,
            "serializer_fields": (),
        },
        "recipient_country": {
            "fields": "recipient_country",
            "queryset": Country.objects.all(),
            "serializer": CountrySerializer,
            "serializer_fields": ('url', 'code', 'name', 'location'),
        },
        "recipient_region": {
            "fields": "recipient_region",
            "queryset": Region.objects.all(),
            "serializer": RegionSerializer,
            "serializer_fields": ('url', 'code', 'name', 'location'),
        },
        "sector": {
            "fields": "sector",
            "queryset": Sector.objects.all(),
            "serializer": SectorSerializer,
            "serializer_fields": ('url', 'code', 'name'),
        },
        "reporting_organisation": {
            "fields": (("reporting_organisations__normalized_ref", "ref"),),
            "queryset": ActivityReportingOrganisation.objects.all(),
            "serializer": None,
            "serializer_fields": (),
        },
        "participating_organisation": {
            "fields": (("participating_organisations__normalized_ref", "ref") , ("participating_organisations__primary_name", "name"),),
            "queryset": ActivityParticipatingOrganisation.objects.all(),
            "serializer": None,
            "serializer_fields": (), # has default serializer_fields
        },
        "document_link_category": {
            "fields": (('documentlink__categories__code', 'document_link_category'),),
            "queryset": DocumentCategory.objects.all(),
            "serializer": CodelistSerializer,
            "serializer_fields": (), # has default serializer_fields
        },
        "activity_status": {
            "fields": "activity_status",
            "queryset": ActivityStatus.objects.all(),
            "serializer": CodelistSerializer,
            "serializer_fields": (), # has default serializer_fields
        },
        "policy_marker": {
            "fields": "policy_marker",
            "queryset": PolicyMarker.objects.all(),
            "serializer": CodelistSerializer,
            "serializer_fields": (), # has default serializer_fields
        },
        "collaboration_type": {
            "fields": "collaboration_type",
            "queryset": CollaborationType.objects.all(),
            "serializer": CodelistSerializer,
            "serializer_fields": (), # has default serializer_fields
        },
        "default_flow_type": {
            "fields": "default_flow_type",
            "queryset": FlowType.objects.all(),
            "serializer": CodelistSerializer,
            "serializer_fields": (), # has default serializer_fields
        },
        "default_aid_type": {
            "fields": "default_aid_type",
            "queryset": AidType.objects.all(),
            "serializer": CodelistSerializer,
            "serializer_fields": (), # has default serializer_fields
        },
        "default_finance_type": {
            "fields": "default_finance_type",
            "queryset": FinanceType.objects.all(),
            "serializer": CodelistSerializer,
            "serializer_fields": (), # has default serializer_fields
        },
        "default_tied_status": {
            "fields": "default_tied_status",
            "queryset": TiedStatus.objects.all(),
            "serializer": CodelistSerializer,
            "serializer_fields": (), # has default serializer_fields
        },
        "budget_per_year": {
            "fields": "year",
            "extra": { 
                'year': 'EXTRACT(YEAR FROM "period_start")::integer',
            },
            "queryset": None,
            "serializer": None,
            "serializer_fields": (),
        },
        "budget_per_quarter": {
            "fields": ("year","quarter"),
            "extra": {
                'year': 'EXTRACT(YEAR FROM "period_start")::integer',
                'quarter': 'EXTRACT(QUARTER FROM "period_start")::integer',
            },
            "queryset": None,
            "serializer": None,
            "serializer_fields": (),
        },
        "transaction_date_year": {
            "fields": "year",
            "extra": {
                'year': 'EXTRACT(YEAR FROM "transaction_date")::integer',
            },
            "queryset": None,
            "serializer": None,
            "serializer_fields": (),
        },
        "transactions_per_quarter": {
            "fields": ("year", "quarter"),
            "extra": {
                'year': 'EXTRACT(YEAR FROM "transaction_date")::integer',
                'quarter': 'EXTRACT(QUARTER FROM "transaction_date")::integer',
            },
            "queryset": None,
            "serializer": None,
            "serializer_fields": (),
        },
    }

    _allowed_orderings = [ i['fields'] for i in _allowed_groupings.values()]
    _allowed_orderings = []
    for grouping in _allowed_groupings.values():
        if type(grouping['fields']) is str:
            _allowed_orderings.append(grouping['fields'])
        else: 
            for field in grouping['fields']: # assume it is a tuple
                if type(field) is str:
                    _allowed_orderings.append(field)
                else:
                    _allowed_orderings.append(field[1]) # renamed

    def apply_order_filters(self, queryset, orderList, aggregationList):

        allowed_orderings = self._allowed_orderings + aggregationList
        allowed_orderings = allowed_orderings + ['-' + o for o in allowed_orderings]

        orderings = self._intersection(allowed_orderings, orderList)
        ordered_orderings = [order for order in orderList if order in allowed_orderings]

        if (len(orderings)):
            return queryset.order_by(*ordered_orderings)
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

        before_annotations = dict() # before values()
        after_annotations = dict() # after values()

        same_query_aggregations = [i for i in aggregationList if not self._aggregations[i].get('extra_filter')]
        separate_aggregations = [i for i in aggregationList if self._aggregations[i].get('extra_filter')]

        for aggregation in same_query_aggregations:
            a = self._aggregations.get(aggregation, {})
            after_annotations[a['annotate_name']] = a['annotate']
     
        # aggregations that can be performed in the same query (hence require no extra filters)
        groupings = {group: self._allowed_groupings[group] for group in groupList}
        groupFields = []

        for grouping in groupings.values():
            fields = grouping['fields']
            if type(fields) is str:
                groupFields.append(fields)
            else: # is a tuple like ((actual, renamed), (actual, renamed), actual, actual) for example
                for field in fields:
                    if type(field) is str:
                        groupFields.append(field)
                    else: # is a tuple like (actual, renamed)
                        groupFields.append(field[1]) # append the renamed to values(), must annotate actual->rename
                        before_annotations[field[1]] = F(field[0]) # use F, see https://docs.djangoproject.com/en/1.7/ref/models/queries/#django.db.models.F

        groupExtras = {"select": grouping["extra"] for grouping in groupings.values() if "extra" in grouping}

        queryset = queryset.annotate(**before_annotations)
        first_queryset = queryset

        # apply extras
        first_queryset = first_queryset.extra(**groupExtras)
        queryset = first_queryset.extra(**groupExtras)

        # remove nulls (
        # to do: check why values() uses left outer joins,
        # this can be a lot slower than inner joins and will prevent the null
        nullFilters = {}
        for grouping in groupings.values():
            if grouping["serializer_fields"]:
                nullFilters[grouping["field"] + '__isnull'] = False
        for aggregation in same_query_aggregations:
            nullFilters[aggregation + '__isnull'] = False
            if 'no_null_check' in self._aggregations[aggregation]:
                nullFilters = {}

        # Apply group_by calls and annotations
        result = first_queryset.values(*groupFields).annotate(**after_annotations).filter(**nullFilters)

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
            serializer_fields = self._allowed_groupings[grouping]["serializer_fields"]
            foreignQueryset = self._allowed_groupings[grouping]["queryset"]

            if serializer:
                data = serializer(foreignQueryset,
                    context={
                        'request': request,
                    },
                    many=True,
                    fields=serializer_fields,
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
            'count':len(result),
            'results': result
        }

    def _union(self, list1, list2):
        return list(set(list1) | set(list2))

    def _intersection(self, list1, list2):
        return list(set(list1) & set(list2))
