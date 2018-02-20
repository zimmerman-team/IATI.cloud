from django.db.models import query, Q
import operator

from django.db.models import Prefetch


class TransactionQuerySet(query.QuerySet):
    class Meta:
        DEFAULT_SEARCH_FIELDS = ('description',)
        SEARCHABLE_PROPERTIES = {
            'description': {
                'name': 'description',
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

    def prefetch_all(self):
        return self.prefetch_activity() \
                .prefetch_description() \
                .prefetch_provider_organisation() \
                .prefetch_receiver_organisation() \
                .prefetch_transaction_type() \
                .prefetch_currency() \
                .prefetch_disbursement_channel() \
                .prefetch_flow_type() \
                .prefetch_finance_type() \
                .prefetch_aid_type() \
                .prefetch_tied_status() \
                .prefetch_sector() \
                .prefetch_recipient_country() \
                .prefetch_recipient_region()

    def prefetch_activity(self):
        from iati.models import Narrative

        return self.select_related('activity__title').prefetch_related(
            Prefetch(
                'activity__title__narratives',
                queryset=Narrative.objects.all()
                .select_related('language'))
        )
        # return self.select_related('activity')

    def prefetch_currency(self):
        return self.select_related('currency')

    def prefetch_transaction_type(self):
        return self.select_related('transaction_type')

    def prefetch_description(self):
        from iati.models import Narrative

        return self.prefetch_related(
            Prefetch(
                'description__narratives',
                queryset=Narrative.objects.all()
                .select_related('language')
            )
        )

    def prefetch_provider_organisation(self):
        from iati.transaction.models import TransactionProvider
        from iati.models import Narrative
        narrative_prefetch = Prefetch('narratives', queryset=Narrative.objects.select_related('language'))

        return self.prefetch_related(
            Prefetch(
                'provider_organisation',
                queryset=TransactionProvider.objects.all()
                .select_related('organisation')
                .select_related('provider_activity')
                .prefetch_related(narrative_prefetch)),
        )

    def prefetch_receiver_organisation(self):
        from iati.transaction.models import TransactionReceiver
        from iati.models import Narrative
        narrative_prefetch = Prefetch('narratives', queryset=Narrative.objects.select_related('language'))

        return self.prefetch_related(
            Prefetch(
                'receiver_organisation',
                queryset=TransactionReceiver.objects.all()
                .select_related('organisation')
                .select_related('receiver_activity')
                .prefetch_related(narrative_prefetch)),
        )

    def prefetch_disbursement_channel(self):
        return self.select_related('disbursement_channel')

    def prefetch_flow_type(self):
        return self.select_related('flow_type')

    def prefetch_finance_type(self):
        return self.select_related('finance_type')

    def prefetch_aid_type(self):
        return self.select_related('aid_type')

    def prefetch_tied_status(self):
        return self.select_related('tied_status')

    def prefetch_sector(self):
        return self.prefetch_related('transaction_sector')

    def prefetch_recipient_country(self):
        return self.prefetch_related('transaction_recipient_country')

    def prefetch_recipient_region(self):
        return self.prefetch_related('transaction_recipient_region')
