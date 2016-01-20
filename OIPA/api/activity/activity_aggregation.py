from operator import itemgetter

from django.db.models import Count
from django.db.models import Sum
from django.db.models import Q, F
from django.db.models.functions import Coalesce
from django.db import connection

from rest_framework.serializers import BaseSerializer

from geodata.models import Country
from geodata.models import Region
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
        "sector_percentage_weighted_incoming_fund": {
            "field": "incoming_fund",
            "extra_filter": Q(transaction__transaction_type=1),
            "annotate_name": 'incoming_fund',
            "annotate": (Coalesce(Sum('transaction__value'), 0) * Coalesce('activitysector__percentage', 100) / 100),
            "has_subquery": ''.join([
                'select sector_id as sector, ',
                'sum(incoming_fund) as incoming_fund from ({}) as "temptab" ',
                'group by "sector_id" ',
                'order by "sector_id"'])
        },
        "recipient_country_percentage_weighted_incoming_fund": {
            "field": "incoming_fund",
            "extra_filter": Q(transaction__transaction_type=1),
            "annotate_name": 'incoming_fund',
            "annotate": (Coalesce(Sum('transaction__value'), 0) * Coalesce('activityrecipientcountry__percentage', 100) / 100),
            "has_subquery": ''.join([
                'select country_id as recipient_country, ',
                'sum(incoming_fund) as incoming_fund ',
                'from ({}) as "temptab" ',
                'group by "country_id" ',
                'order by "country_id"'])
        },
        "sector_percentage_weighted_disbursement": {
            "field": "disbursement",
            "extra_filter": Q(transaction__transaction_type=3),
            "annotate_name": 'disbursement',
            "annotate": (Coalesce(Sum('transaction__value'), 0) * Coalesce('activitysector__percentage', 100) / 100),
            "has_subquery": ''.join([
                'select sector_id as sector, ',
                'sum(disbursement) as disbursement ',
                'from ({}) as "temptab" ',
                'group by "sector_id" ',
                'order by "sector_id"'])
        },
        "recipient_country_percentage_weighted_disbursement": {
            "field": "disbursement",
            "extra_filter": Q(transaction__transaction_type=3),
            "annotate_name": 'disbursement',
            "annotate": (Coalesce(Sum('transaction__value'), 0) * Coalesce('activityrecipientcountry__percentage', 100) / 100),
            "has_subquery": ''.join([
                'select country_id as recipient_country, ',
                'sum(disbursement) as disbursement ',
                'from ({}) as "temptab" ',
                'group by "country_id" ',
                'order by "country_id"'])
        },
        "sector_percentage_weighted_budget": {
            "field": "budget",
            "annotate_name": 'total_budget_per_percentage',
            "annotate": (Coalesce(Sum('budget__value'), 0) * Coalesce('activitysector__percentage', 100) / 100),
            "has_subquery": ''.join([
                'select sector_id as sector, ',
                'sum(total_budget_per_percentage) as budget ',
                'from ({}) as "temptab" ',
                'group by "sector_id" ',
                'order by "sector_id"'])
        },
        "location_disbursement": {
            "field": "weighted_country_value",
            "annotate_name": 'value_by_country',
            "annotate": (Coalesce(Sum('location__value'), 0) * Coalesce('activitysector__percentage', 100) / 100),
            "has_subquery": ''.join([
                'select loc_country_id, ',
                'sum(value_by_country) as total_value, ',
                'region_id, country_name ',
                'from ({}) as per_activity ',
                'group by per_activity.loc_country_id'])
        }
    }

    _allowed_groupings = {
        "related_activity": {
            "fields": (("relatedactivity__ref_activity__id", 'activity_id'),),
            "queryset": None,
            "serializer": None,
            "serializer_fields": (),
        },
        "recipient_country": {
            "fields": "recipient_country",
            "queryset": Country,
            "serializer": CountrySerializer,
            "serializer_fields": ('url', 'code', 'name', 'location'),
        },
        "recipient_region": {
            "fields": "recipient_region",
            "queryset": Region,
            "serializer": RegionSerializer,
            "serializer_fields": ('url', 'code', 'name', 'location'),
        },
        "sector": {
            "fields": "sector",
            "queryset": Sector,
            "serializer": SectorSerializer,
            "serializer_fields": ('url', 'code', 'name'),
        },
        "reporting_organisation": {
            "fields": (("reporting_organisations__normalized_ref", "ref"),),
            "queryset": ActivityReportingOrganisation,
            "serializer": None,
            "serializer_fields": (),
        },
        "participating_organisation": {
            "fields": (("participating_organisations__normalized_ref", "ref"),
                       ("participating_organisations__primary_name", "name"),),
            "queryset": ActivityParticipatingOrganisation,
            "serializer": None,
            "serializer_fields": (),
        },
        "document_link_category": {
            "fields": (('documentlink__categories__code', 'document_link_category'),),
            "queryset": DocumentCategory,
            "serializer": CodelistSerializer,
            "serializer_fields": (),
        },
        "activity_status": {
            "fields": "activity_status",
            "queryset": ActivityStatus,
            "serializer": CodelistSerializer,
            "serializer_fields": (),
        },
        "policy_marker": {
            "fields": "policy_marker",
            "queryset": PolicyMarker,
            "serializer": CodelistSerializer,
            "serializer_fields": (),
        },
        "collaboration_type": {
            "fields": "collaboration_type",
            "queryset": CollaborationType,
            "serializer": CodelistSerializer,
            "serializer_fields": (),
        },
        "default_flow_type": {
            "fields": "default_flow_type",
            "queryset": FlowType,
            "serializer": CodelistSerializer,
            "serializer_fields": (),
        },
        "default_aid_type": {
            "fields": "default_aid_type",
            "queryset": AidType,
            "serializer": CodelistSerializer,
            "serializer_fields": (),
        },
        "default_finance_type": {
            "fields": "default_finance_type",
            "queryset": FinanceType,
            "serializer": CodelistSerializer,
            "serializer_fields": (),
        },
        "default_tied_status": {
            "fields": "default_tied_status",
            "queryset": TiedStatus,
            "serializer": CodelistSerializer,
            "serializer_fields": (),
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
            "fields": ("year", "quarter"),
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

    def get_order_filters(self, order_list):

        allowed_orderings = []
        for grouping in self._allowed_groupings.values():
            if isinstance(grouping['fields'], str):
                allowed_orderings.append(grouping['fields'])
            else:
                for field in grouping['fields']: # assume it is a tuple
                    if isinstance(field, str):
                        allowed_orderings.append(field)
                    else:
                        allowed_orderings.append(field[1]) # renamed
        for aggregation in self._aggregations.values():
            if isinstance(aggregation['field'], str):
                allowed_orderings.append(aggregation['field'])

        allowed_orderings = allowed_orderings + ['-' + o for o in allowed_orderings]

        ordered_orderings = [order for order in order_list if order in allowed_orderings]

        return ordered_orderings

    def apply_limit_offset_filters(self, results, page_size, page):

        if page_size:

            if not page:
                page = 1

            page_size = int(page_size)
            page = int(page)

            offset = (page * page_size) - page_size
            offset_plus_limit = offset + page_size
            return results[offset:offset_plus_limit]

        return results

    def apply_annotations(self, queryset, group_list, aggregation_list):

        # before values()
        before_annotations = dict()
        # after values()
        after_annotations = dict()

        same_query_aggregations = [i for i in aggregation_list if not self._aggregations[i].get('extra_filter')]
        separate_aggregations = [i for i in aggregation_list if self._aggregations[i].get('extra_filter')]

        for aggregation in same_query_aggregations:
            aggregation_meta = self._aggregations.get(aggregation, {})
            after_annotations[aggregation_meta['annotate_name']] = aggregation_meta['annotate']

        # aggregations that can be performed in the same query (hence require no extra filters)
        groupings = {group: self._allowed_groupings[group] for group in group_list}
        group_fields = []
        null_filters = {}

        for grouping in groupings.values():
            fields = grouping['fields']
            if isinstance(fields, str):
                group_fields.append(fields)
                if not grouping.get('extra'):
                    null_filters[fields + '__isnull'] = False
            # is a tuple like ((actual, renamed), (actual, renamed), actual, actual) for example
            else:
                for field in fields:
                    if isinstance(field, str):
                        group_fields.append(field)
                        if not grouping.get('extra'):
                            null_filters[field + '__isnull'] = False
                    # is a tuple like (actual, renamed)
                    else:
                        # append the renamed to values(), must annotate actual->rename
                        group_fields.append(field[1])
                        if not grouping.get('extra'):
                            null_filters[field[1] + '__isnull'] = False
                        # use F, see https://docs.djangoproject.com/en/1.7/ref/models/queries/#django.db.models.F
                        before_annotations[field[1]] = F(field[0])

        group_extras = {"select": grouping["extra"] for grouping in groupings.values() if "extra" in grouping}

        # apply extras
        queryset = queryset.annotate(**before_annotations).extra(**group_extras)

        # Apply group_by calls and annotations
        result = queryset.filter(**null_filters).values(*group_fields).annotate(**after_annotations)

        # aggregations that require extra filters, and hence must be executed separately
        for aggregation in separate_aggregations:

            aggregation_meta = self._aggregations.get(aggregation, None)
            extra_filter = aggregation_meta["extra_filter"]
            field = aggregation_meta["field"]
            annotation = dict([(aggregation_meta['annotate_name'], aggregation_meta['annotate'])])

            # one query
            if len(same_query_aggregations) is 0:
                result = queryset.filter(extra_filter).filter(**null_filters).values(*group_fields).annotate(**annotation)
                continue

            next_result = queryset.filter(extra_filter).filter(**null_filters).values(*group_fields).annotate(**annotation)

            main_group_field = group_fields[0]

            # make dict of next result
            result_dict = {}
            for next_item in iter(next_result):
                result_dict[next_item[main_group_field]] = next_item[field]

            # join on existing result, set 0 on non existing
            for item in iter(result):
                if item[main_group_field] in result_dict:
                    item[field] = result_dict[item[main_group_field]]
                else:
                    item[field] = 0

            # to do; current functionality assumes the initial result contains all items
            # not sure if that's a valid assumption.

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

        return results

    def serialize_foreign_keys(self, results, request, group_list):

        serializers = {}
        groupfield_list = []

        for grouping in group_list:
            serializer = self._allowed_groupings[grouping]["serializer"]
            serializer_fields = self._allowed_groupings[grouping]["serializer_fields"]
            foreign_queryset = self._allowed_groupings[grouping]["queryset"]

            fields = self._allowed_groupings[grouping]["fields"]

            this_grouping_field_list = []

            if isinstance(fields, str):
                this_grouping_field_list.append(fields)
            else:
                for field in fields:
                    if isinstance(field, str):
                        this_grouping_field_list.append(field)
                    else:
                        this_grouping_field_list.append(field[1])

            groupfield_list.extend(this_grouping_field_list)

            if serializer:
                data = serializer(
                    foreign_queryset.objects.all(),
                    context={
                        'request': request,
                    },
                    many=True,
                    fields=serializer_fields).data

                serializers[grouping] = {str(i.get('code')): i for i in data}
            else:

                for field in this_grouping_field_list:
                    serializers[field] = {}
                    for i in results:
                        value = i.get(field)
                        if isinstance(value, unicode):
                            value = value.encode('utf-8')
                        serializers[field][value] = value

        for i, result in enumerate(list(results)):
            for key, value in result.iteritems():
                if key in groupfield_list:
                    if value is not None:
                        if isinstance(value, unicode):
                            value = value.encode('utf-8')
                        result[key] = serializers.get(key, {}).get(value)
                    else:
                        del results[i]
                        break

        return results

    def apply_ordering(self, result, orderings):
        # python order functionality
        if len(orderings):
            # can only order by 1 key atm
            order = orderings[0]
            result_list = list(result)
            descending = False
            if order[0] == '-':
                descending = True
                order = order[1:]

            result = sorted(result_list, key=itemgetter(order))

            if descending:
                result = list(reversed(result))

        return result

    def to_representation(self, queryset):
        # remove default orderings
        queryset = queryset.order_by()

        request = self.context.get('request')
        params = request.query_params

        order_by = filter(None, params.get('order_by', "").split(','))
        page_size = params.get('page_size', None)
        page = params.get('page', None)

        group_by = self._intersection(
            filter(
                None,
                params.get('group_by', "").split(',')),
            self._allowed_groupings.keys())

        aggregations = self._intersection(
            filter(None,
                   params.get('aggregations', "").split(',')),
            self._aggregations.keys())

        if not len(group_by):
            return {'error_message': "Invalid value for mandatory field 'group_by'"}
        elif not len(aggregations):
            return {'error_message': "Invalid value for mandatory field 'aggregations'"}

        # queryset = self.apply_group_filters(queryset, request, group_by)
        orderings = self.get_order_filters(order_by)
        queryset = self.apply_annotations(queryset, group_by, aggregations)

        # After this, a valuesQuerySet
        result = self.apply_extra_calculations(queryset, aggregations)
        result = self.apply_ordering(result, orderings)
        result = self.apply_limit_offset_filters(result, page_size, page)

        # after this, an array
        result = [a for a in result]
        result = self.serialize_foreign_keys(result, request, group_by)

        if page_size:
            count = len(queryset)
        else:
            count = len(result)

        return {
            'count': count,
            'results': result
        }

    def _union(self, list1, list2):
        return list(set(list1) | set(list2))

    def _intersection(self, list1, list2):
        return list(set(list1) & set(list2))
