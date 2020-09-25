import django_filters

from geodata.models import Country

from api.generics.filters import CommaSeparatedCharFilter

class CountryFilter(django_filters.FilterSet):
    """
    Filter countries list
    """
    region_code = django_filters.NumberFilter(
        field_name='region__code'
    )
    name = CommaSeparatedCharFilter(
        field_name='name',
        lookup_expr='in'
    )

    class Meta:
        model = Country
        fields = [
            'code',
            'name',
            'region_code']
