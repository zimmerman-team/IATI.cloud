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
            "extra_filter": {'transaction__transaction_type': 3},
            "annotate_name": 'disbursement',
            "annotate": Sum('transaction__value'),
        },
        "expenditure": {
            "field": "expenditure",
            "extra_filter": {'transaction__transaction_type': 4},
            "annotate_name": "expenditure",
            "annotate": Sum('transaction__value')
        },
        "commitment": {
            "field": "commitment",
            "extra_filter": {'transaction__transaction_type': 2},
            "annotate_name": 'commitment',
            "annotate": Sum('transaction__value')
        },
        "incoming_fund": {
            "field": "incoming_fund",
            "extra_filter": {'transaction__transaction_type': 1},
            "annotate_name": 'incoming_fund',
            "annotate": Sum('transaction__value')
        },
        "transaction_value": {
            "field": "value",
            "annotate_name": 'value',
            "annotate": Sum('transaction__value')
        },
        "recipient_country_percentage_weighted_incoming_fund": {
            "field": "incoming_fund",
            "extra_filter": {'transaction__transaction_type': 1},
            "annotate_name": 'incoming_fund',
            "annotate": (
                Coalesce(Sum('transaction__value'), 0) * Coalesce('activityrecipientcountry__percentage', 100) / 100),
            "has_subquery": ''.join([
                'select country_id as recipient_country, ',
                'sum(incoming_fund) as incoming_fund ',
                'from ({}) as "temptab" ',
                'group by "country_id" ',
                'order by "country_id"']),
            "required_group_by": "recipient_country"
        },
        "recipient_country_percentage_weighted_disbursement": {
            "field": "disbursement",
            "extra_filter": {'transaction__transaction_type': 3},
            "annotate_name": 'disbursement',
            "annotate": (
                Coalesce(Sum('transaction__value'), 0) * Coalesce('activityrecipientcountry__percentage', 100) / 100),
            "has_subquery": ''.join([
                'select country_id as recipient_country, ',
                'sum(disbursement) as disbursement ',
                'from ({}) as "temptab" ',
                'group by "country_id" ',
                'order by "country_id"']),
            "required_group_by": "recipient_country"
        },
        "recipient_country_percentage_weighted_expenditure": {
            "field": "expenditure",
            "extra_filter": {'transaction__transaction_type': 4},
            "annotate_name": 'expenditure',
            "annotate": (
                Coalesce(Sum('transaction__value'), 0) * Coalesce('activityrecipientcountry__percentage', 100) / 100),
            "has_subquery": ''.join([
                'select country_id as recipient_country, ',
                'sum(expenditure) as expenditure ',
                'from ({}) as "temptab" ',
                'group by "country_id" ',
                'order by "country_id"']),
            "required_group_by": "recipient_country"
        },
        "sector_percentage_weighted_incoming_fund": {
            "field": "incoming_fund",
            "extra_filter": {'transaction__transaction_type': 1},
            "annotate_name": 'incoming_fund',
            "annotate": (
                Coalesce(Sum('transaction__value'), 0) * Coalesce('activitysector__percentage', 100) / 100),
            "has_subquery": ''.join([
                'select sector_id as sector, ',
                'sum(incoming_fund) as incoming_fund from ({}) as "temptab" ',
                'group by "sector_id" ',
                'order by "sector_id"']),
            "required_group_by": "sector"
        },
        "sector_percentage_weighted_disbursement": {
            "field": "disbursement",
            "extra_filter": {'transaction__transaction_type': 3},
            "annotate_name": 'disbursement',
            "annotate": (
                Coalesce(Sum('transaction__value'), 0) * Coalesce('activitysector__percentage', 100) / 100),
            "has_subquery": ''.join([
                'select sector_id as sector, ',
                'sum(disbursement) as disbursement ',
                'from ({}) as "temptab" ',
                'group by "sector_id" ',
                'order by "sector_id"']),
            "required_group_by": "sector"
        },
        "sector_percentage_weighted_expenditure": {
            "field": "expenditure",
            "extra_filter": {'transaction__transaction_type': 4},
            "annotate_name": 'expenditure',
            "annotate": (
                Coalesce(Sum('transaction__value'), 0) * Coalesce('activitysector__percentage', 100) / 100),
            "has_subquery": ''.join([
                'select sector_id as sector, ',
                'sum(expenditure) as expenditure ',
                'from ({}) as "temptab" ',
                'group by "sector_id" ',
                'order by "sector_id"']),
            "required_group_by": "sector"
        },
        "sector_percentage_weighted_budget": {
            "field": "budget",
            "annotate_name": 'total_budget_per_percentage',
            "annotate": (
                Coalesce(Sum('budget__value'), 0) * Coalesce('activitysector__percentage', 100) / 100),
            "has_subquery": ''.join([
                'select sector_id as sector, ',
                'sum(total_budget_per_percentage) as budget ',
                'from ({}) as "temptab" ',
                'group by "sector_id" ',
                'order by "sector_id"']),
            "required_group_by": "sector"
        },
    }

    _allowed_groupings = {
        "related_activity": {
            "fields": (("relatedactivity__ref_activity__id", 'activity_id'),),
            "queryset": None,
            "serializer": None,
            "serializer_fields": (),
        },
        "recipient_country": {
            "fields": ("recipient_country",),
            "queryset": Country,
            "serializer": CountrySerializer,
            "serializer_fields": ('url', 'code', 'name', 'location'),
        },
        "recipient_region": {
            "fields": ("recipient_region",),
            "queryset": Region,
            "serializer": RegionSerializer,
            "serializer_fields": ('url', 'code', 'name', 'location'),
        },
        "sector": {
            "fields": ("sector",),
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
        "transaction_provider_org_narrative": {
            "fields": (("transaction__provider_organisation__narratives__content", "name"),
                       ("transaction__transaction_type__code", "transaction_type")),
            "queryset": None,
            "serializer": None,
            "serializer_fields": (),
        },
        "transaction_receiver_org_narrative": {
            "fields": (("transaction__receiver_organisation__narratives__content", "name"),
                       ("transaction__transaction_type__code", "transaction_type")),
            "queryset": None,
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
            "fields": ("activity_status",),
            "queryset": ActivityStatus,
            "serializer": CodelistSerializer,
            "serializer_fields": (),
        },
        "policy_marker": {
            "fields": ("policy_marker",),
            "queryset": PolicyMarker,
            "serializer": CodelistSerializer,
            "serializer_fields": (),
        },
        "collaboration_type": {
            "fields": ("collaboration_type",),
            "queryset": CollaborationType,
            "serializer": CodelistSerializer,
            "serializer_fields": (),
        },
        "default_flow_type": {
            "fields": ("default_flow_type",),
            "queryset": FlowType,
            "serializer": CodelistSerializer,
            "serializer_fields": (),
        },
        "default_aid_type": {
            "fields": ("default_aid_type",),
            "queryset": AidType,
            "serializer": CodelistSerializer,
            "serializer_fields": (),
        },
        "default_finance_type": {
            "fields": ("default_finance_type",),
            "queryset": FinanceType,
            "serializer": CodelistSerializer,
            "serializer_fields": (),
        },
        "default_tied_status": {
            "fields": ("default_tied_status",),
            "queryset": TiedStatus,
            "serializer": CodelistSerializer,
            "serializer_fields": (),
        },
        "budget_per_year": {
            "fields": ("year",),
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
            "fields": ("year",),
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
        """Order the result by 1 or multiple keys."""

        allowed_orderings = []
        for grouping in self._allowed_groupings.values():
            # assume it is a tuple
            for field in grouping['fields']:
                if isinstance(field, str):
                    allowed_orderings.append(field)
                else:
                    # renamed
                    allowed_orderings.append(field[1])

        for aggregation in self._aggregations.values():
            if isinstance(aggregation['field'], str):
                allowed_orderings.append(aggregation['field'])

        allowed_orderings = allowed_orderings + ['-' + o for o in allowed_orderings]

        ordered_orderings = [order for order in order_list if order in allowed_orderings]

        return ordered_orderings

    def apply_limit_offset_filters(self, results, page_size, page):
        """
        limit the results to the amount set by page_size

        The results are all queried so this gives at most a small performance boost
        because there's less data to serialize.
        """

        if page_size:

            if not page:
                page = 1

            page_size = int(page_size)
            page = int(page)

            offset = (page * page_size) - page_size
            offset_plus_limit = offset + page_size
            return results[offset:offset_plus_limit]

        return results

    @staticmethod
    def get_group_key(item, group_fields, has_multiple_group_keys):
            if not has_multiple_group_keys:
                return item[group_fields[0]]
            else:
                # res = '__'.join([item[group_field].encode('utf-8') for group_field in group_fields])
                group_keys = []
                for group_field in group_fields:
                    if isinstance(item[group_field], int):
                        group_keys.append(str(item[group_field]))
                    if isinstance(item[group_field], unicode):
                        group_keys.append(item[group_field].encode('utf-8'))
                return '__'.join(group_keys)

    def apply_annotations(self, queryset, group_list, aggregation_list):
        """
        Builds and performs the query, when multiple aggregations were requested it joins the results

        """

        separate_aggregations = [i for i in aggregation_list]

        groupings = {group: self._allowed_groupings[group] for group in group_list}
        group_fields = []
        result_dict = None

        # before values()
        before_annotations = dict()
        after_filters = {}

        for grouping in groupings.values():
            fields = grouping['fields']

            if 'after_filters' in grouping:
                after_filters[grouping['after_filters'][0]] = grouping['after_filters'][1]

            for field in fields:
                if isinstance(field, str):
                    group_fields.append(field)
                # is a tuple like (actual, renamed)
                else:
                    # append the renamed to values(), must annotate actual->rename
                    group_fields.append(field[1])
                    # use F, see https://docs.djangoproject.com/en/1.9/ref/models/expressions/#f-expressions
                    before_annotations[field[1]] = F(field[0])

        # apply extras
        group_extras = {"select": grouping["extra"] for grouping in groupings.values() if "extra" in grouping}
        queryset = queryset.annotate(**before_annotations).extra(**group_extras)

        # preparation for aggregation look
        main_group_key = group_fields[0]
        has_multiple_group_keys = len(main_group_key) - 1
        aggregation_key_dict = {}

        for index, aggregation in enumerate(separate_aggregations):
            key = self._aggregations[aggregation]['field']
            aggregation_key_dict[key] = 0

        # execute all aggregations separately and join their results
        for index, aggregation in enumerate(separate_aggregations):

            aggregation_meta = self._aggregations[aggregation]
            aggregation_key = aggregation_meta['field']
            annotation = dict([(aggregation_meta['annotate_name'], aggregation_meta['annotate'])])
            extra_filter = aggregation_meta.get('extra_filter', {})

            next_result = queryset.filter(**extra_filter).values(*group_fields).annotate(**annotation).filter(**after_filters)

            if aggregation_meta.get('has_subquery'):
                next_result = self.apply_subquery(next_result, aggregation_meta)

            # no results yet, make a dict of the results
            if index is 0:
                result_dict = {}
                for item in iter(next_result):
                    group_key = self.get_group_key(item, group_fields, has_multiple_group_keys)
                    result_dict[group_key] = aggregation_key_dict.copy()
                    result_dict[group_key][aggregation_key] = item[aggregation_key]
                    for group_field in group_fields:
                        result_dict[group_key][group_field] = item[group_field]
                continue

            # else, join next result on the result dictionary, result key does not exist yet, create it
            for item in iter(next_result):
                group_key = self.get_group_key(item, group_fields, has_multiple_group_keys)
                if group_key not in result_dict:
                    result_dict[group_key] = aggregation_key_dict.copy()
                    for group_field in group_fields:
                        result_dict[group_key][group_field] = item[group_field]

                result_dict[group_key][aggregation_key] = item[aggregation_key]

        return list(result_dict.values())

    def apply_subquery(self, results, aggregation_meta):
        """
        Performs a required subquery

        parameters:
        result              - Queryset
        aggregation_meta    - the current _aggregations met

        Sub-queries are not supported in Django. Therefore these are performed in raw sql queries.
        this function uses the _aggregations.has_subquery field to perform the query.
        """
        sql, params = results.query.sql_with_params()
        cursor = connection.cursor()
        cursor.execute(
            aggregation_meta.get('has_subquery').format(sql),
            params)

        def dict_fetchall(cursor):
            columns = [col[0] for col in cursor.description]
            return [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]

        return dict_fetchall(cursor)

    def serialize_foreign_keys(self, results, request, group_list):
        """
        Re-use serializers to show full info of the grouped by items.

        Not all group by keys are serialized, this is based upon the value at _groupings.serializer
        """

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
        """
        orders a list by a key

        parameters
        result    - list of results
        orderings - list of order keys
        """

        if len(orderings):

            # handle reverse, reverse all if any order is reversed,
            # could be improved by allowing combinations of reversed, non-reversed
            reverse = False

            for index, order in enumerate(orderings):
                if order[0] == '-':
                    reverse = True
                    orderings[index] = order[1:]

            orderings_tuple = tuple(orderings)
            result = sorted(result, key=itemgetter(*orderings_tuple), reverse=reverse)

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

        orderings = self.get_order_filters(order_by)
        queryset = self.apply_annotations(queryset, group_by, aggregations)

        # from here, queryset is a list
        result = self.apply_ordering(queryset, orderings)
        result = self.apply_limit_offset_filters(result, page_size, page)

        result = [a for a in result]
        result = self.serialize_foreign_keys(result, request, group_by)

        count = len(queryset)

        return {
            'count': count,
            'results': result
        }

    def _intersection(self, list1, list2):
        return list(set(list1) & set(list2))
