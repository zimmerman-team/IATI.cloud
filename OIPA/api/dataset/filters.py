from api.generics.filters import CommaSeparatedCharFilter
from iati_synchroniser.models import IatiXmlSource
from django_filters import FilterSet, CharFilter, NumberFilter


class DatasetFilter(FilterSet):
    """
    Filter countries list
    """

    ref = CommaSeparatedCharFilter(
        lookup_type='in')

    source_type = CommaSeparatedCharFilter(
        lookup_type='in',
        name='type')

    publisher = CommaSeparatedCharFilter(
        lookup_type='in',
        name='publisher__org_id')

    note_exception_type = CharFilter(
        lookup_type='icontains',
        name='iatixmlsourcenote__exception_type')

    note_field = CharFilter(
        lookup_type='icontains',
        name='iatixmlsourcenote__field')

    note_count_gte = NumberFilter(
        lookup_type='gte',
        name='note_count')

    class Meta:
        model = IatiXmlSource
