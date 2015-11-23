from django.db.models import query, Q
from geodata.models import Region
from django.db.models import Sum
import operator

from django.db.models import Prefetch


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

    def prefetch_default_aid_type(self):
        return self.select_related('default_aid_type__category')

    def prefetch_default_finance_type(self):
        return self.select_related('default_finance_type__category')


    def prefetch_participating_organisations(self):
        from iati.models import ActivityParticipatingOrganisation, Narrative
        narrative_prefetch = Prefetch('narratives', queryset=Narrative.objects.select_related('language'))

        return self.prefetch_related(
            Prefetch('participating_organisations',
                queryset=ActivityParticipatingOrganisation.objects.all()\
                        .select_related('type', 'role')\
                        .prefetch_related(narrative_prefetch)),
        )

    def prefetch_reporting_organisations(self):
        from iati.models import ActivityParticipatingOrganisation, ActivityReportingOrganisation, Narrative
        narrative_prefetch = Prefetch('narratives', queryset=Narrative.objects.select_related('language'))

        return self.prefetch_related(
            Prefetch('reporting_organisations',
                queryset=ActivityReportingOrganisation.objects.all()\
                        .select_related('type')\
                        .prefetch_related(narrative_prefetch)),
        )

    def prefetch_recipient_countries(self):
        from iati.models import ActivityRecipientCountry, Narrative

        return self.prefetch_related(
            Prefetch('activityrecipientcountry_set',
                queryset=ActivityRecipientCountry.objects.all()\
                    .select_related('country').defer('country__polygon'))
        )

    def prefetch_recipient_regions(self):
        from iati.models import ActivityRecipientRegion, Narrative

        return self.prefetch_related(
            Prefetch('activityrecipientregion_set',
                queryset=ActivityRecipientRegion.objects.all()\
                    .select_related('region') \
                    .select_related('vocabulary')
                    )
        )

    def prefetch_sectors(self):
        from iati.models import ActivitySector, Narrative

        return self.prefetch_related(
            Prefetch('activitysector_set',
                queryset=ActivitySector.objects.all()\
                    .select_related('sector') \
                    .select_related('vocabulary')
                    )
        )

    def prefetch_activity_dates(self):
        from iati.models import ActivityDate

        return self.prefetch_related(
            Prefetch('activitydate_set',
                queryset=ActivityDate.objects.all()\
                    .select_related('type')
                    )
        )

    def prefetch_policy_markers(self):
        from iati.models import ActivityPolicyMarker, Narrative
        narrative_prefetch = Prefetch('narratives', queryset=Narrative.objects.select_related('language'))

        return self.prefetch_related(
            Prefetch('activitypolicymarker_set',
                queryset=ActivityPolicyMarker.objects.all()\
                    .select_related('code', 'vocabulary', 'significance')\
                    .prefetch_related(narrative_prefetch)
                    )
        )

    def prefetch_budgets(self):
        from iati.models import Budget, Narrative

        return self.prefetch_related(
            Prefetch('budget_set',
                queryset=Budget.objects.all()\
                    .select_related('type', 'currency')
                    )
        )

    def prefetch_description(self):
        from iati.models import Description, Narrative
        narrative_prefetch = Prefetch('narratives', queryset=Narrative.objects.select_related('language'))

        return self.prefetch_related(
            Prefetch('description_set',
                queryset=Description.objects.all()\
                    .select_related('type')\
                    .prefetch_related(narrative_prefetch)
                    )
        )

    def prefetch_document_links(self):
        from iati.models import DocumentLink, DocumentLinkCategory

        # TODO: fix category prefetch, not working
        category_prefetch = Prefetch('documentlinkcategory_set',
            queryset=DocumentLinkCategory.objects.all()\
                .select_related('category'))

        return self.prefetch_related(
            Prefetch('documentlink_set',
                queryset=DocumentLink.objects.all()\
                    .select_related('file_format')\
                    .prefetch_related(category_prefetch)
                    )
        )

    def prefetch_results(self):
        from iati.models import Result, Narrative

        return self.prefetch_related(
            Prefetch('result_set',
                queryset=Result.objects.all()\
                    .select_related('type')
                    )
        )

    def prefetch_locations(self):
        from iati.models import Location, Narrative
        narrative_prefetch = Prefetch('narratives', queryset=Narrative.objects.select_related('language'))
        print('called prefetch')

        return self.prefetch_related(
            Prefetch('location_set',
                queryset=Location.objects.all()\
                    .select_related('location_reach')\
                    .select_related('location_id_vocabulary')\
                    .select_related('location_class')\
                    .select_related('feature_designation')\
                    .select_related('exactness')\
                    )
        )

    def prefetch_related_activities(self):
        from iati.models import RelatedActivity

        return self.prefetch_related(
            Prefetch('relatedactivity_set',
                queryset=RelatedActivity.objects.all()\
                    .select_related('type')
                    )
        )

    def prefetch_title(self):
        from iati.models import Narrative

        return self.prefetch_related(
            Prefetch('title__narratives',
                queryset=Narrative.objects.all()\
                    .select_related('language')
                    )
        )

    def aggregate_budget(self):
        sum = self.aggregate(
            budget=Sum('budget__value')
        ).get('budget', 0.00)
        return sum

    def aggregate_expenditure(self):
        queryset = self.filter(transaction__transaction_type__code='4')
        sum = queryset.aggregate(
            expenditure=Sum('transaction__value')
        ).get('expenditure', 0.00)
        return sum

    def aggregate_disbursement(self):
        queryset = self.filter(transaction__transaction_type__code='3')
        sum = queryset.aggregate(
            disbursement=Sum('transaction__value')
        ).get('disbursement', 0.00)
        return sum

    def aggregate_commitment(self):
        queryset = self.filter(transaction__transaction_type__code='2')
        sum = queryset.aggregate(
            commitment=Sum('transaction__value')
        ).get('commitment', 0.00)
        return sum

    def aggregate_incoming_fund(self):
        queryset = self.filter(transaction__transaction_type='1')
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
