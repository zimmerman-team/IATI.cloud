from api.generics.filters import CommaSeparatedCharFilter, TogetherFilterSet
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

    class Meta:
        model = Organisation
        fields = []
