from api.generics.filters import (
    BooleanFilter, CommaSeparatedCharFilter, TogetherFilterSet
)
from iati_organisation.models import Organisation


class OrganisationFilter(TogetherFilterSet):
    # naming is according to IATI standard.
    reporting_organisation_identifier = CommaSeparatedCharFilter(
        field_name='organisation_identifier',
        lookup_expr='in'
    )
    name = CommaSeparatedCharFilter(
        field_name='primary_name',
        lookup_expr='exact'
    )
    is_reporting_organisation = BooleanFilter(
        field_name='activityreportingorganisation',
        lookup_expr='isnull',
        exclude=True)

    class Meta:
        model = Organisation
        fields = []
