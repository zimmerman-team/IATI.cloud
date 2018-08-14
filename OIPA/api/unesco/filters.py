from django_filters import NumberFilter
from api.generics.filters import (
    CommaSeparatedCharFilter,
    TogetherFilterSet,
    ToManyFilter,
    StartsWithInCommaSeparatedCharFilter,
)
from iati.models import (
    ActivityRecipientCountry,
    ActivityRecipientRegion,
    ActivitySector,
    ActivityParticipatingOrganisation
)
from unesco.models import TransactionBalance


class TransactionBalanceFilter(TogetherFilterSet):

    reporting_organisation_identifier = CommaSeparatedCharFilter(
        name='activity__publisher__publisher_iati_id',
        lookup_expr='in')

    recipient_country = ToManyFilter(
        qs=ActivityRecipientCountry,
        lookup_expr='in',
        name='country__code',
        fk='activity')

    recipient_region = ToManyFilter(
        qs=ActivityRecipientRegion,
        lookup_expr='in',
        name='region__code',
        fk='activity')

    sector = ToManyFilter(
        qs=ActivitySector,
        lookup_expr='in',
        name='sector__code',
        fk='activity')

    participating_organisation_name = ToManyFilter(
        qs=ActivityParticipatingOrganisation,
        lookup_expr='in',
        name='primary_name',
        fk='activity')

    sector_startswith_in = StartsWithInCommaSeparatedCharFilter(
        lookup_expr='startswith',
        name='activity__sector__code')

    total_budget_lte = NumberFilter(
        lookup_expr='lte',
        name='total_budget')

    total_budget_gte = NumberFilter(
        lookup_expr='gte',
        name='total_budget')

    total_expenditure_lte = NumberFilter(
        lookup_expr='lte',
        name='total_expenditure')

    total_expenditure_gte = NumberFilter(
        lookup_expr='gte',
        name='total_expenditure')

    activity_status = CommaSeparatedCharFilter(
        lookup_expr='in',
        name='activity_status')

    class Meta:
        model = TransactionBalance
        fields = '__all__'
