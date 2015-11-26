from django.db.models import query
from django.db.models import Sum
from django.db.models import Prefetch


class ActivityQuerySet(query.QuerySet):

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
        from iati.models import Result

        return self.prefetch_related(
            Prefetch(
                'result_set',
                queryset=Result.objects.all()
                .select_related('type'))
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


