import django_filters
from geodata.models import Country


class CountryFilter(django_filters.FilterSet):
    """
    Filter countries list
    """
    region_code = django_filters.NumberFilter(name='region__code')

    class Meta:
        model = Country
        fields = [
            'code',
            'name',
            'region_code',
        ]
