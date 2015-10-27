from django.db.models import Count
from django.db.models import Sum
from django.db.models import Q
from django.db.models.functions import Coalesce

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
from iati.models import ActivityReportingOrganisation

from api.activity.serializers import CodelistSerializer
from api.activity.serializers import ParticipatingOrganisationSerializer
from api.activity.serializers import ReportingOrganisationSerializer
from api.country.serializers import CountrySerializer
from api.region.serializers import RegionSerializer
from api.sector.serializers import SectorSerializer


class ActivityAggregationSerializer(BaseSerializer):

    _aggregations = {
        "count": {
            "field": "count",
            "annotate_name": "count",
            "annotate": Count('id')
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
            "extra_filter": Q(transaction__transaction_type='D'),
            "annotate_name": 'disbursement',
            "annotate": Sum('transaction__value'),
        },
        "expenditure": {
            "field": "expenditure",
            "extra_filter": Q(transaction__transaction_type='E'),
            "annotate_name": "expenditure",
            "annotate": Sum('transaction__value')
        },
        "commitment": {
            "field": "commitment",
            "extra_filter": Q(transaction__transaction_type='C'),
            "annotate_name": 'commitment',
            "annotate": Sum('transaction__value')
        },
        "incoming_fund": {
            "field": "incoming_fund",
            "extra_filter": Q(transaction__transaction_type='IF'),
            "annotate_name": 'incoming_fund',
            "annotate": Sum('transaction__value')
        },
        "sector_percentage_weighted_budget": {
            "field": "weighted_budget",
            "annotate_name": 'sector_percentage_weighted_budget',
            "annotate": Sum(Coalesce('activitysector__percentage', 100) * Coalesce('activity_aggregations__total_budget_value', 0) / 100),
            "no_null_check": True
        }
    }

    _allowed_groupings = {
        "recipient_country": {
            "field": "recipient_country",
            "queryset": Country.objects.all(),
            "serializer": CountrySerializer,
            "fields": ('url', 'code', 'name'),
            # "subquery": "SELECT * FROM geodata_country WHERE geodata_country.code = recipient_country",
        },
        "recipient_region": {
            "field": "recipient_region",
            "queryset": Region.objects.all(),
            "serializer": RegionSerializer,
            "fields": ('url', 'code', 'name'),
        },
        "sector": {
            "field": "sector",
            "queryset": Sector.objects.all(),
            "serializer": SectorSerializer,
            "fields": ('url', 'code', 'name'),
        },
        "reporting_organisation": {
            "field": "reporting_organisations__ref",
            "queryset": ActivityReportingOrganisation.objects.all(),
            "serializer": ReportingOrganisationSerializer,
            "fields": ('ref',),
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
            "fields": None,
        },
        "budget_per_quarter": {
            "field": "year,quarter",
            "extra": {
                'year': 'EXTRACT(YEAR FROM "period_start")::integer',
                'quarter': 'EXTRACT(QUARTER FROM "period_start")::integer',
            },
            "queryset": None,
            "serializer": None,
            "fields": None,
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

        same_query_aggregations = [ i for i in aggregationList if not self._aggregations[i].get('extra_filter') ]
        separate_aggregations = [ i for i in aggregationList if self._aggregations[i].get('extra_filter') ]

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
        # for grouping in groupings:
        first_queryset = first_queryset.extra(**groupExtras)

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

        # aggregations that require extra filters, and hence must be exectued separately
        for aggregation in separate_aggregations:
            # field = self._aggregations.get("")
            a = self._aggregations.get(aggregation, None)
            extra_filter = a["extra_filter"]
            field = a["field"]

            annotation = dict([(a['annotate_name'], a['annotate'])])
            next_result = queryset.filter(extra_filter).values(*groupList).annotate(**annotation)
            
            main_group_field = groupList[0]


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

    def serialize_foreign_keys(self, valuesQuerySet, request, groupList):

        serializers = {}

        for grouping in groupList:
            field_name = self._allowed_groupings[grouping]["field"]
            serializer = self._allowed_groupings[grouping]["serializer"]
            fields = self._allowed_groupings[grouping]["fields"]
            foreignQueryset = self._allowed_groupings[grouping]["queryset"]

            if serializer:
                if fields:
                    data = serializer(foreignQueryset,
                        context={
                            'request': request,
                        },
                        many=True,
                        fields=fields,
                    ).data
                else:
                    data = serializer(foreignQueryset,
                        context={
                            'request': request,
                        },
                        many=True,
                    ).data

                serializers[grouping] = { i.get('code'):i for i in data }


        results = list(valuesQuerySet)

        for i, result in enumerate(list(results)):
            for k,v in result.iteritems():
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

        if not (len(group_by) and len(aggregations)):
            return {'error_message': 'Please provide (valid values for) both mandatory fields; group_by and aggregations'}

        # queryset = self.apply_group_filters(queryset, request, group_by)
        queryset = self.apply_order_filters(queryset, order_by, aggregations)
        queryset = self.apply_annotations(queryset, group_by, aggregations)
        result = self.apply_limit_offset_filters(queryset, page_size, page)
        result = self.serialize_foreign_keys(result, request, group_by)

        return {
            'count':len(result),
            'results': result
        }

    def _union(self, list1, list2):
        return list(set(list1) | set(list2))

    def _intersection(self, list1, list2):
        return list(set(list1) & set(list2))