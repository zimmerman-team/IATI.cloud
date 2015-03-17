from django.db.models import query, Q
from geodata.models import Region
from django.db.models import Sum
import operator


class ActivityQuerySet(query.QuerySet):
    class Meta:
        DEFAULT_SEARCH_FIELDS = ('titles', 'descriptions', 'identifiers')
        SEARCHABLE_PROPERTIES = {
            'identifiers': {
                'name': 'activitysearchdata__search_identifier',
                'method': ''
            },
            'titles': {
                'name': 'activitysearchdata__search_title',
                'method': '__search'
            },
            'descriptions': {
                'name': 'activitysearchdata__search_description',
                'method': '__search'
            },
            'countries': {
                'name': 'activitysearchdata__search_country_name',
                'method': '__search'
            },
            'regions': {
                'name': 'activitysearchdata__search_region_name',
                'method': '__search'
            },
            'sectors': {
                'name': 'activitysearchdata__search_sector_name',
                'method': '__search'
            },
            'part_organisations': {
                'name': 'activitysearchdata__search_participating_organisation_name',
                'method': '__search'
            },
            'rep_organisations': {
                'name': 'activitysearchdata__search_reporting_organisation_name',
                'method': '__search'
            },
            'documents': {
                'name': 'activitysearchdata__search_documentlink_title',
                'method': '__search'
            },
            'other_identifiers': {
                'name': 'otheridentifier__identifier',
                'method': ''
            },
        }

    def search(self, query, search_fields):
        prepared_filter = self._prepare_search_filter(
            self.Meta.DEFAULT_SEARCH_FIELDS if search_fields is None
            else search_fields, query
        )
        return self.filter(reduce(
            operator.or_, [Q(f) for f in prepared_filter]
        ))

    def distinct_if_necessary(self, applicable_filters):
        for key in applicable_filters:
            if key[-4:] == '__in':
                return self.distinct()
        return self
    distinct_if_necessary.queryset_only = True

    def filter_years(self, years):
        prepared_filter = []

        try:
            for f in years:
                prepared_filter.append(Q(start_planned__year=f))
        except TypeError:
            prepared_filter.append(Q(start_planned__year=years))

        if len(prepared_filter) > 1:
            return self.filter(
                reduce(operator.or_, prepared_filter)
            ).distinct()
        else:
            return self.filter(prepared_filter[0])

    def aggregate_total_budget(self):
        sum = self.aggregate(
            total_budget=Sum('total_budget')
        ).get('total_budget', 0.00)
        return sum

    def aggregate_expenditure(self):
        queryset = self.filter(transaction__transaction_type='E')
        sum = queryset.aggregate(
            expenditure=Sum('transaction__value')
        ).get('expenditure', 0.00)
        return sum

    def aggregate_disbursement(self):
        queryset = self.filter(transaction__transaction_type='D')
        sum = queryset.aggregate(
            disbursement=Sum('transaction__value')
        ).get('disbursement', 0.00)
        return sum

    def aggregate_commitment(self):
        queryset = self.filter(transaction__transaction_type='C')
        sum = queryset.aggregate(
            commitment=Sum('transaction__value')
        ).get('commitment', 0.00)
        return sum

    def aggregate_incoming_fund(self):
        queryset = self.filter(transaction__transaction_type='IF')
        sum = queryset.aggregate(
            incoming_fund=Sum('transaction__value')
        ).get('incoming_fund', 0.00)
        return sum

    def aggregate_title(self):
        queryset = self.exclude(title__isnull=True)
        return queryset.count()

    def _create_full_text_query(self, query):
        """
        Modifies the query for full text search boolean mode.
        This adds a + and * char to each word. + sets boolean AND search.
        * activates wildcard search
        """
        fts_query = ''
        for word in query.split():
            fts_query = "{0}+{1}* ".format(fts_query, word)
        fts_query = fts_query[:-1]
        return fts_query

    def _prepare_search_filter(self, search_fields, query):
        fts_query = self._create_full_text_query(query)
        prepared_filter = []
        for field in search_fields:
            if field in self.Meta.SEARCHABLE_PROPERTIES:
                property = self.Meta.SEARCHABLE_PROPERTIES.get(field)
                prepared_filter.append((
                    property.get('name') + property.get('method'),
                    fts_query if property.get('method') == '__search'
                    else query
                ))
            else:
                raise Exception(
                    'unsupported search_field. Choices are: {0}'.format(
                        str(self.Meta.SEARCHABLE_PROPERTIES.keys())
                    )
                )
        return prepared_filter

    def in_region(self, pk):
        region = Region.objects.get(pk=pk)
        return self.filter(recipient_region__in=region.get_self_and_subregions())
