from django_filters import NumberFilter
from api.generics.filters import (
    CommaSeparatedCharFilter,
    TogetherFilterSet,
    StartsWithInCommaSeparatedCharFilter,
)
from unesco.models import TransactionBalance


class TransactionBalanceFilter(TogetherFilterSet):

    reporting_organisation_identifier = CommaSeparatedCharFilter(
        name='activity__publisher__publisher_iati_id',
        lookup_expr='in')

    recipient_country = CommaSeparatedCharFilter(
        lookup_expr='in',
        name='activity__recipient_country__code')

    recipient_region = CommaSeparatedCharFilter(
        lookup_expr='in',
        name='activity__recipient_region__code')

    sector = CommaSeparatedCharFilter(
        lookup_expr='in',
        name='activity__sector__code')

    participating_organisation_name = CommaSeparatedCharFilter(
        lookup_expr='in',
        name='activity__participating_organisations__primary_name')

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
        name='activity__activity_status')

    class Meta:
        model = TransactionBalance
        fields = '__all__'
