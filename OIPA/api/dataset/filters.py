import django_filters
from iati_synchroniser.models import IatiXmlSource


class DatasetFilter(django_filters.FilterSet):
    """
    Filter countries list
    """
    # region_code = django_filters.NumberFilter(name='region__code')

    class Meta:
        model = IatiXmlSource
        fields = [
            'ref',
            'type',]
