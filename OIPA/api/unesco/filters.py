from django_filters import (
    NumberFilter,
    DateFilter
)
from api.generics.filters import (
    CommaSeparatedCharFilter,
    TogetherFilterSet,
    StartsWithInCommaSeparatedCharFilter,
)
from unesco.models import TransactionBalance


class TransactionBalanceFilter(TogetherFilterSet):

    reporting_organisation_identifier = CommaSeparatedCharFilter(
        field_name='activity__publisher__publisher_iati_id',
        lookup_expr='in')

    recipient_country = CommaSeparatedCharFilter(
        lookup_expr='in',
        name='activity__recipient_country__code')

    recipient_region = CommaSeparatedCharFilter(
        lookup_expr='in',
        field_name='activity__recipient_region__code')

    sector = CommaSeparatedCharFilter(
        lookup_expr='in',
        field_name='activity__sector__code')

    participating_organisation_name = CommaSeparatedCharFilter(
        lookup_expr='in',
        field_name='activity__participating_organisations__primary_name')

    sector_startswith_in = StartsWithInCommaSeparatedCharFilter(
        lookup_expr='startswith',
        field_name='activity__sector__code')

    total_budget_lte = NumberFilter(
        lookup_expr='lte',
        field_name='total_budget')

    total_budget_gte = NumberFilter(
        lookup_expr='gte',
        field_name='total_budget')

    total_expenditure_lte = NumberFilter(
        lookup_expr='lte',
        field_name='total_expenditure')

    total_expenditure_gte = NumberFilter(
        lookup_expr='gte',
        field_name='total_expenditure')

    activity_status = CommaSeparatedCharFilter(
        lookup_expr='in',
        field_name='activity__activity_status')

    planned_start_date_lte = DateFilter(
        lookup_expr='lte',
        field_name='activity__planned_start')

    planned_start_date_gte = DateFilter(
        lookup_expr='gte',
        field_name='activity__planned_start')

    planned_end_date_lte = DateFilter(
        lookup_expr='lte',
        field_name='activity__planned_end')

    planned_end_date_gte = DateFilter(
        lookup_expr='gte',
        field_name='activity__planned_end')

    class Meta:
        model = TransactionBalance
        fields = '__all__'
