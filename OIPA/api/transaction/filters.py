from django_filters import FilterSet, NumberFilter, DateFilter, BooleanFilter
from api.generics.filters import CommaSeparatedCharFilter
from api.generics.filters import ToManyFilter

from api.activity.filters import ActivityFilter

from iati.models import *
from iati.transaction.models import *

class TransactionFilter(FilterSet):
    """
    Transaction filter class
    """

    type = CommaSeparatedCharFilter(
        name='transaction_type',
        lookup_type='in')

    currency = CommaSeparatedCharFilter(
        name='currency',
        lookup_type='in')

    date_year = NumberFilter(
        lookup_type='year',
        name='transaction_date'
    )

    min_value = NumberFilter(name='value', lookup_type='gte')
    max_value = NumberFilter(name='value', lookup_type='lte')


    provider_activity = ToManyFilter(
        qs=TransactionProvider,
        lookup_type='in',
        name='provider_activity_ref',
        fk='transaction',
    )

    provider_organisation_name = ToManyFilter(
        qs=TransactionProvider,
        lookup_type='in',
        name='narratives__content',
        fk='transaction',
    )

    receiver_organisation_name = ToManyFilter(
        qs=TransactionReceiver,
        lookup_type='in',
        name='narratives__content',
        fk='transaction',
    )

    #
    # Activity filters...
    #

    activity_id = CommaSeparatedCharFilter(
        name='activity__id',
        lookup_type='in')

    activity_scope = CommaSeparatedCharFilter(
        name='activity__scope__code',
        lookup_type='in',)

    activity_recipient_region_not_in = CommaSeparatedCharFilter(
        lookup_type='in',
        name='activity__recipient_region',
        exclude=True,)

    activity_planned_start_date_lte = DateFilter(
        lookup_type='lte',
        name='activity__planned_start')

    activity_planned_start_date_gte = DateFilter(
        lookup_type='gte',
        name='activity__planned_start')

    activity_actual_start_date_lte = DateFilter(
        lookup_type='lte',
        name='activity__actual_start')

    activity_actual_start_date_gte = DateFilter(
        lookup_type='gte',
        name='activity__actual_start')

    activity_planned_end_date_lte = DateFilter(
        lookup_type='lte',
        name='activity__planned_end')

    activity_planned_end_date_gte = DateFilter(
        lookup_type='gte',
        name='activity__planned_end')

    activity_actual_end_date_lte = DateFilter(
        lookup_type='lte',
        name='activity__actual_end')

    activity_actual_end_date_gte = DateFilter(
        lookup_type='gte',
        name='activity__actual_end')

    activity_end_date_lte = DateFilter(
        lookup_type='lte',
        name='activity__end_date')

    activity_end_date_gte = DateFilter(
        lookup_type='gte',
        name='activity__end_date')

    activity_start_date_lte = DateFilter(
        lookup_type='lte',
        name='activity__start_date')

    activity_start_date_gte = DateFilter(
        lookup_type='gte',
        name='activity__start_date')

    activity_end_date_isnull = BooleanFilter(name='activity__end_date__isnull')
    activity_start_date_isnull = BooleanFilter(name='activity__start_date__isnull')

    activity_xml_source_ref = CommaSeparatedCharFilter(
        lookup_type='in',
        name='activity__xml_source_ref',)

    activity_activity__status = CommaSeparatedCharFilter(
        lookup_type='in',
        name='activity__activity_status',)

    activity_hierarchy = CommaSeparatedCharFilter(
        lookup_type='in',
        name='activity__hierarchy',)

    activity_budget_period_start = DateFilter(
        lookup_type='gte',
        name='activity__budget__period_start',)

    activity_budget_period_end = DateFilter(
        lookup_type='lte',
        name='activity__budget__period_end')

    activity_related_activity_id = ToManyFilter(
	main_fk='activity',
        qs=RelatedActivity,
        fk='current_activity',
        lookup_type='in',
        name='ref_activity__id',
    )

    activity_related_activity_type = ToManyFilter(
	main_fk='activity',
        qs=RelatedActivity,
        lookup_type='in',
        name='type__code',
        fk='current_activity',
    )

    activity_related_activity_recipient_country = ToManyFilter(
	main_fk='activity',
        qs=RelatedActivity,
        lookup_type='in',
        name='ref_activity__recipient_country',
        fk='current_activity',
    )

    activity_related_activity_recipient_region = ToManyFilter(
	main_fk='activity',
        qs=RelatedActivity,
        lookup_type='in',
        name='ref_activity__recipient_region',
        fk='current_activity',
    )

    activity_related_activity_sector = ToManyFilter(
	main_fk='activity',
        qs=RelatedActivity,
        lookup_type='in',
        name='ref_activity__sector',
        fk='current_activity',
    )

    activity_related_activity_sector_category = ToManyFilter(
	main_fk='activity',
        qs=RelatedActivity,
        lookup_type='in',
        name='ref_activity__sector__category',
        fk='current_activity',
    )

    activity_budget_currency = ToManyFilter(
	main_fk='activity',
        qs=Budget,
        lookup_type='in',
        name='currency__code',
        fk='activity',
    )

    activity_recipient_country = ToManyFilter(
	main_fk='activity',
        qs=ActivityRecipientCountry,
        lookup_type='in',
        name='country__code',
        fk='activity',
    )

    activity_recipient_region = ToManyFilter(
	main_fk='activity',
        qs=ActivityRecipientRegion,
        lookup_type='in',
        name='region__code',
        fk='activity',
    )
    activity_sector = ToManyFilter(
	main_fk='activity',
        qs=ActivitySector,
        lookup_type='in',
        name='sector__code',
        fk='activity',
    )

    activity_sector_category = ToManyFilter(
	main_fk='activity',
        qs=ActivitySector,
        lookup_type='in',
        name='sector__category__code',
        fk='activity',
    )

    activity_participating_organisation = ToManyFilter(
	main_fk='activity',
        qs=ActivityParticipatingOrganisation,
        lookup_type='in',
        name='normalized_ref',
        fk='activity',
    )

    activity_participating_organisation_name = ToManyFilter(
	main_fk='activity',
        qs=ActivityParticipatingOrganisation,
        lookup_type='in',
        name='primary_name',
        fk='activity',
    )

    activity_participating_organisation_role = ToManyFilter(
	main_fk='activity',
        qs=ActivityParticipatingOrganisation,
        lookup_type='in',
        name='role__code',
        fk='activity',
    )

    activity_participating_organisation_type = ToManyFilter(
	main_fk='activity',
        qs=ActivityParticipatingOrganisation,
        lookup_type='in',
        name='type__code',
        fk='activity',
    )

    activity_reporting_organisation = ToManyFilter(
	main_fk='activity',
        qs=ActivityReportingOrganisation,
        lookup_type='in',
        name='normalized_ref',
        fk='activity',
    )

    # TODO: degrades performance very badly, should probably remove this - 2016-03-02
    activity_reporting_organisation_startswith = ToManyFilter(
	main_fk='activity',
        qs=ActivityReportingOrganisation,
        lookup_type='startswith',
        name='normalized_ref',
        fk='activity',
    )

    class Meta:
        model = Transaction
        fields = [
            'id',
            'aid_type',
            'transaction_type',
            'value',
            'min_value',
            'max_value',
        ]

