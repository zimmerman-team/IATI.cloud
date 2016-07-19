from django.db import models
from django.db.models import Prefetch
from djorm_pgfulltext.models import SearchManagerMixIn, SearchQuerySet


class ActivityQuerySet(SearchQuerySet):

    # TODO: this makes counting a lot slower than it has to be for a lot of queries
    def count(self):
        self = self.order_by().only('id')
        return super(ActivityQuerySet, self).count()

    # TODO: fix import conflicts - 2016-01-18
    def prefetch_all(self):

        return self.prefetch_default_aid_type() \
            .prefetch_default_finance_type() \
            .prefetch_participating_organisations() \
            .prefetch_reporting_organisations() \
            .prefetch_recipient_countries() \
            .prefetch_recipient_regions() \
            .prefetch_sectors() \
            .prefetch_activity_dates() \
            .prefetch_policy_markers() \
            .prefetch_budgets() \
            .prefetch_title() \
            .prefetch_descriptions() \
            .prefetch_document_links() \
            .prefetch_results() \
            .prefetch_locations() \
            .prefetch_related_activities() \
            .prefetch_aggregations()

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


    def prefetch_title(self):
        from iati.models import Narrative

        return self.prefetch_related(
            Prefetch(
                'title__narratives',
                queryset=Narrative.objects.all()
                .select_related('language'))
        )

    def prefetch_descriptions(self):
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
                .prefetch_related(
                    'resultindicatorperiodtargetlocation_set', 
                    'resultindicatorperiodactuallocation_set', 
                    'resultindicatorperiodtargetdimension_set',
                    'resultindicatorperiodactualdimension_set',
                    period_target_comment_prefetch, 
                    period_actual_comment_prefetch)
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
        from iati.models import Location, LocationName, LocationDescription, LocationAdministrative
        from iati.models import LocationActivityDescription, Narrative, GeographicVocabulary

        narrative_prefetch = Prefetch(
            'narratives',
            queryset=Narrative.objects.all().select_related('language'))

        location_name_prefetch = Prefetch(
            'locationname_set',
            queryset=LocationName.objects.all()
            .prefetch_related(narrative_prefetch))

        location_administrative_prefetch = Prefetch(
            'locationadministrative_set',
            queryset=LocationAdministrative.objects.all()
            .select_related('vocabulary'))


        location_description_prefetch = Prefetch(
            'locationdescription_set',
            queryset=LocationDescription.objects.all()
            .prefetch_related(narrative_prefetch))

        location_activity_description_prefetch = Prefetch(
            'locationactivitydescription_set',
            queryset=LocationActivityDescription.objects.all()
            .prefetch_related(narrative_prefetch))

        return self.prefetch_related(
            Prefetch(
                'location_set',
                queryset=Location.objects.all()
                .select_related('location_reach', 'location_id_vocabulary', 'location_class', 'feature_designation__category', 'exactness')
                .prefetch_related(
                    location_name_prefetch,
                    location_administrative_prefetch,
                    location_description_prefetch,
                    location_activity_description_prefetch
                ))
        )

    def prefetch_related_activities(self):
        from iati.models import RelatedActivity

        return self.prefetch_related(
            Prefetch(
                'relatedactivity_set',
                queryset=RelatedActivity.objects.all()
                .select_related('type'))
        )

    def prefetch_contact_info(self):
        from iati.models import ContactInfo, Narrative

        organisation_prefetch = Prefetch(
            'organisation__narratives',
            queryset=Narrative.objects.all()
            .select_related('language'))

        department_prefetch = Prefetch(
            'department__narratives',
            queryset=Narrative.objects.all()
            .select_related('language'))

        person_name_prefetch = Prefetch(
            'person_name__narratives',
            queryset=Narrative.objects.all()
            .select_related('language'))

        job_title_prefetch = Prefetch(
            'job_title__narratives',
            queryset=Narrative.objects.all()
            .select_related('language'))

        mailing_address_prefetch = Prefetch(
            'mailing_address__narratives',
            queryset=Narrative.objects.all()
            .select_related('language'))

        return self.prefetch_related(
            Prefetch(
                'contactinfo_set',
                queryset=ContactInfo.objects.all()
                .select_related('type', 'organisation', 'department', 'person_name', 'job_title', 'mailing_address')
                .prefetch_related(organisation_prefetch, department_prefetch, person_name_prefetch, job_title_prefetch, mailing_address_prefetch))
        )


    # def prefetch_transactions(self):
    #     from iati.transaction.models import Transaction

    #     # TODO: Nullable foreign keys do not get prefetched in select_related() call - 2016-01-20
    #     return self.prefetch_related(
    #         Prefetch(
    #             'transaction_set',
    #             queryset=Transaction.objects.all() \
    #             .select_related('transaction_type')
    #             .select_related('currency')
    #             .select_related('disbursement_channel')
    #             .select_related('flow_type')
    #             .select_related('finance_type')
    #             .select_related('aid_type')
    #             .select_related('tied_status')
    #             .prefetch_all()
    #         )
    #     )

    def prefetch_aggregations(self):
        from iati.models import ActivityAggregation, ChildAggregation, ActivityPlusChildAggregation

        return self.prefetch_related(
                'activity_aggregation',
                'child_aggregation',
                'activity_plus_child_aggregation',
        )


class ActivityManager(SearchManagerMixIn, models.Manager):

    """Activity manager with search capabilities"""
    
    def get_queryset(self):
        return ActivityQuerySet(self.model, using=self._db)
        
        
