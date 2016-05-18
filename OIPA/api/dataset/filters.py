from api.generics.filters import CommaSeparatedCharFilter
from iati_synchroniser.models import IatiXmlSource
from django_filters import FilterSet


class DatasetFilter(FilterSet):
    """
    Filter countries list
    """

    publisher = CommaSeparatedCharFilter(
        lookup_type='in',
        name='publisher__org_id')

    class Meta:
        model = IatiXmlSource
        fields = [
            'ref',
            'type',]
