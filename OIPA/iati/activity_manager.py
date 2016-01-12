from django.db import models
from django.db.models import query
from django.db.models import Sum
from django.db.models import Count
from django.db.models import Prefetch

# from common.util import adapt
from djorm_pgfulltext.models import SearchManagerMixIn, SearchQuerySet

class ActivityQuerySet(SearchQuerySet):

    # def search(self, query, dictionary='simple', raw=False, fields=None):
    #     """Search using Postgres full text search

    #     :query: query string
    #     :returns: queryset

    #     """
    #     if not query: return self

    #     qs = self
        
    #     function = "to_tsquery" if raw else "plainto_tsquery"
    #     ts_query = "{func}('{dictionary}', {query})".format({
    #         func: function,
    #         dictionary: dictionary,
    #         query: adapt(query) 
    #     })

    #     where = "({search_vector}) @@ {ts_query}".format({
    #         search_vector: ,
    #         ts_query: ts_query
    #     })

    #     qs = qs.extra(where=ts_query)

    # TODO: this makes counting a lot slower than it has to be for a lot of queries
    def count(self):
        # self = self.order_by().only('id')
        # return self.queryset.select_related('activitysearch').annotate(count=Count('id', distinct=True)).count()
        self = self.values('id', 'activitysearch').distinct('id')
        return super(ActivityQuerySet, self).count()

    def prefetch_default_aid_type(self):
        return self.select_related('default_aid_type__category')

    def prefetch_default_finance_type(self):
        return self.select_related('default_finance_type__category')

    def prefetch_participating_organisations(self):
        from iati.models import ActivityParticipatingOrganisation, Narrative
        narrative_prefetch = Prefetch(
            'narratives',
            queryset=Narrative.objects.select_related('language'))

        return self.prefetch_related(
            Prefetch(
                'participating_organisations',
                queryset=ActivityParticipatingOrganisation.objects.all()
                .select_related('type', 'role')
                .prefetch_related(narrative_prefetch)),)

    def prefetch_reporting_organisations(self):
        from iati.models import ActivityReportingOrganisation, Narrative
        narrative_prefetch = Prefetch(
            'narratives',
            queryset=Narrative.objects.select_related('language'))

        return self.prefetch_related(
            Prefetch(
                'reporting_organisations',
                queryset=ActivityReportingOrganisation.objects.all()
                .select_related('type')
                .prefetch_related(narrative_prefetch)),)

    def prefetch_recipient_countries(self):
        from iati.models import ActivityRecipientCountry

        return self.prefetch_related(
            Prefetch(
                'activityrecipientcountry_set',
                queryset=ActivityRecipientCountry.objects.all()
                .select_related('country')
                .defer('country__polygon')))

    def prefetch_recipient_regions(self):
        from iati.models import ActivityRecipientRegion

        return self.prefetch_related(
            Prefetch(
                'activityrecipientregion_set',
                queryset=ActivityRecipientRegion.objects.all()
                .select_related('region')
                .select_related('vocabulary')))

    def prefetch_sectors(self):
        from iati.models import ActivitySector

        return self.prefetch_related(
            Prefetch(
                'activitysector_set',
                queryset=ActivitySector.objects.all()
                .select_related('sector')
                .select_related('vocabulary')))

    def prefetch_activity_dates(self):
        from iati.models import ActivityDate

        return self.prefetch_related(
            Prefetch(
                'activitydate_set',
                queryset=ActivityDate.objects.all()
                .select_related('type')))

    def prefetch_policy_markers(self):
        from iati.models import ActivityPolicyMarker, Narrative
        narrative_prefetch = Prefetch(
            'narratives',
            queryset=Narrative.objects.select_related('language'))

        return self.prefetch_related(
            Prefetch(
                'activitypolicymarker_set',
                queryset=ActivityPolicyMarker.objects.all()
                .select_related('code', 'vocabulary', 'significance')
                .prefetch_related(narrative_prefetch))
        )

    def prefetch_budgets(self):
        from iati.models import Budget

        return self.prefetch_related(
            Prefetch(
                'budget_set',
                queryset=Budget.objects.all()
                .select_related('type', 'currency'))
        )

    def prefetch_description(self):
        from iati.models import Description, Narrative
        narrative_prefetch = Prefetch(
            'narratives',
            queryset=Narrative.objects.select_related('language'))

        return self.prefetch_related(
            Prefetch(
                'description_set',
                queryset=Description.objects.all()
                .select_related('type')
                .prefetch_related(narrative_prefetch))
        )

    def prefetch_document_links(self):
        from iati.models import DocumentLink, DocumentLinkCategory

        # TODO: fix category prefetch, not working
        category_prefetch = Prefetch(
            'documentlinkcategory_set',
            queryset=DocumentLinkCategory.objects.all()
            .select_related('category'))

        return self.prefetch_related(
            Prefetch(
                'documentlink_set',
                queryset=DocumentLink.objects.all()
                .select_related('file_format')
                .prefetch_related(category_prefetch))
        )

    def prefetch_results(self):
        from iati.models import Result, Narrative, ResultIndicatorPeriod, ResultIndicator

        title_prefetch = Prefetch(
            'resulttitle__narratives',
            queryset=Narrative.objects.all()
            .select_related('language'))

        description_prefetch = Prefetch(
            'resultdescription__narratives',
            queryset=Narrative.objects.all()
            .select_related('language'))

        indicator_title_prefetch = Prefetch(
            'resultindicatortitle__narratives',
            queryset=Narrative.objects.all()
            .select_related('language'))

        indicator_description_prefetch = Prefetch(
            'resultindicatordescription__narratives',
            queryset=Narrative.objects.all()
            .select_related('language'))

        period_target_comment_prefetch = Prefetch(
            'resultindicatorperiodtargetcomment__narratives',
            queryset=Narrative.objects.all()
            .select_related('language'))

        period_actual_comment_prefetch = Prefetch(
            'resultindicatorperiodactualcomment__narratives',
            queryset=Narrative.objects.all()
            .select_related('language'))

        indicator_period_prefetch = Prefetch(
            'resultindicatorperiod_set',
            queryset=ResultIndicatorPeriod.objects.all()
                .select_related('result_indicator')
                .prefetch_related(period_target_comment_prefetch, period_actual_comment_prefetch)
        )

        indicator_baseline_comment_prefetch = Prefetch(
            'resultindicatorbaselinecomment__narratives',
            queryset=Narrative.objects.all()
            .select_related('language'))

        indicator_prefetch = Prefetch(
            'resultindicator_set',
            queryset=ResultIndicator.objects.all()
                .select_related('measure')
                .prefetch_related(
                    indicator_title_prefetch, 
                    indicator_description_prefetch,
                    indicator_period_prefetch,
                    indicator_baseline_comment_prefetch
                )
        )

        return self.prefetch_related(
            Prefetch(
                'result_set',
                queryset=Result.objects.all()
                .select_related('type', 'resulttitle', 'resultdescription')
                .prefetch_related(
                    title_prefetch,
                    description_prefetch,
                    indicator_prefetch
                ))
        )

    def prefetch_locations(self):
        from iati.models import Location

        return self.prefetch_related(
            Prefetch(
                'location_set',
                queryset=Location.objects.all()
                .select_related('location_reach')
                .select_related('location_id_vocabulary')
                .select_related('location_class')
                .select_related('feature_designation')
                .select_related('exactness'))
        )

    def prefetch_related_activities(self):
        from iati.models import RelatedActivity

        return self.prefetch_related(
            Prefetch(
                'relatedactivity_set',
                queryset=RelatedActivity.objects.all()
                .select_related('type'))
        )

    def prefetch_title(self):
        from iati.models import Narrative

        return self.prefetch_related(
            Prefetch(
                'title__narratives',
                queryset=Narrative.objects.all()
                .select_related('language'))
        )


class ActivityManager(SearchManagerMixIn, models.Manager):

    """Activity manager with search capabilities"""
    
    def get_queryset(self):
        print('called get_queryset')
        return ActivityQuerySet(self.model, using=self._db).select_related('activitysearch')
        
        
