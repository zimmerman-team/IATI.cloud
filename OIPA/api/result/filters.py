from api.generics.filters import TogetherFilterSet
from api.generics.filters import ToManyFilter
from api.generics.filters import CommaSeparatedCharFilter

from django_filters import DateFilter
from django_filters import BooleanFilter

from iati.models import Result
from iati.models import ResultTitle
from iati.models import ResultIndicatorTitle

from iati.models import *
from iati.transaction.models import *


class ResultFilter(TogetherFilterSet):

    activity_id = CommaSeparatedCharFilter(
        name='activity__id',
        lookup_type='in')

    result_title = ToManyFilter(
        qs=ResultTitle,
        lookup_type='in',
        name='primary_name',
        fk='result',
    )

    indicator_title = ToManyFilter(
        qs=ResultIndicatorTitle,
        lookup_type='in',
        name='primary_name',
        fk='result__indicator',
    )

    # default filters

    activity_scope = CommaSeparatedCharFilter(
        name='activity__scope__code',
        lookup_type='in',)

    planned_start_date_lte = DateFilter(
        lookup_type='lte',
        name='activity__planned_start')

    planned_start_date_gte = DateFilter(
        lookup_type='gte',
        name='activity__planned_start')

    actual_start_date_lte = DateFilter(
        lookup_type='lte',
        name='activity__actual_start')

    actual_start_date_gte = DateFilter(
        lookup_type='gte',
        name='activity__actual_start')

    planned_end_date_lte = DateFilter(
        lookup_type='lte',
        name='activity__planned_end')

    planned_end_date_gte = DateFilter(
        lookup_type='gte',
        name='activity__planned_end')

    actual_end_date_lte = DateFilter(
        lookup_type='lte',
        name='activity__actual_end')

    actual_end_date_gte = DateFilter(
        lookup_type='gte',
        name='activity__actual_end')

    end_date_lte = DateFilter(
        lookup_type='lte',
        name='activity__end_date')

    end_date_gte = DateFilter(
        lookup_type='gte',
        name='activity__end_date')

    start_date_lte = DateFilter(
        lookup_type='lte',
        name='activity__start_date')

    start_date_gte = DateFilter(
        lookup_type='gte',
        name='activity__start_date')

    end_date_isnull = BooleanFilter(name='activity__end_date__isnull')
    start_date_isnull = BooleanFilter(name='activity__start_date__isnull')

    xml_source_ref = CommaSeparatedCharFilter(
        lookup_type='in',
        name='activity__xml_source_ref',)

    activity_status = CommaSeparatedCharFilter(
        lookup_type='in',
        name='activity__activity_status',)

    document_link_category = ToManyFilter(
        main_fk='activity',
        qs=DocumentLink,
        fk='activity',
        lookup_type='in',
        name='categories__code',
    )

    hierarchy = CommaSeparatedCharFilter(
        lookup_type='in',
        name='activity__hierarchy',)

    collaboration_type = CommaSeparatedCharFilter(
        lookup_type='in',
        name='activity__collaboration_type',)

    default_flow_type = CommaSeparatedCharFilter(
        lookup_type='in',
        name='activity__default_flow_type',)

    default_aid_type = CommaSeparatedCharFilter(
        lookup_type='in',
        name='activity__default_aid_type',)

    default_finance_type = CommaSeparatedCharFilter(
        lookup_type='in',
        name='activity__default_finance_type',)

    default_tied_status = CommaSeparatedCharFilter(
        lookup_type='in',
        name='activity__default_tied_status',)

    budget_period_start = DateFilter(
        lookup_type='gte',
        name='activity__budget__period_start',)

    budget_period_end = DateFilter(
        lookup_type='lte',
        name='activity__budget__period_end')

    recipient_country = ToManyFilter(
        main_fk='activity',
        qs=ActivityRecipientCountry,
        lookup_type='in',
        name='country__code',
        fk='activity',
    )

    recipient_region = ToManyFilter(
        main_fk='activity',
        qs=ActivityRecipientRegion,
        lookup_type='in',
        name='region__code',
        fk='activity',
    )

    sector = ToManyFilter(
        main_fk='activity',
        qs=ActivitySector,
        lookup_type='in',
        name='sector__code',
        fk='activity',
    )

    sector_category = ToManyFilter(
        main_fk='activity',
        qs=ActivitySector,
        lookup_type='in',
        name='sector__category__code',
        fk='activity',
    )

    participating_organisation = ToManyFilter(
        main_fk='activity',
        qs=ActivityParticipatingOrganisation,
        lookup_type='in',
        name='normalized_ref',
        fk='activity',
    )

    participating_organisation_name = ToManyFilter(
        main_fk='activity',
        qs=ActivityParticipatingOrganisation,
        lookup_type='in',
        name='primary_name',
        fk='activity',
    )

    participating_organisation_role = ToManyFilter(
        main_fk='activity',
        qs=ActivityParticipatingOrganisation,
        lookup_type='in',
        name='role__code',
        fk='activity',
    )

    participating_organisation_type = ToManyFilter(
        main_fk='activity',
        qs=ActivityParticipatingOrganisation,
        lookup_type='in',
        name='type__code',
        fk='activity',
    )

    reporting_organisation = ToManyFilter(
        main_fk='activity',
        qs=ActivityReportingOrganisation,
        lookup_type='in',
        name='normalized_ref',
        fk='activity',
    )

    class Meta:
        model = Result