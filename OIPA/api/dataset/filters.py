from api.generics.filters import CommaSeparatedCharFilter, ToManyFilter
from iati_synchroniser.models import IatiXmlSource, IatiXmlSourceNote
from django_filters import FilterSet, CharFilter, NumberFilter, DateTimeFilter


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

    note_exception_type = ToManyFilter(
        qs=IatiXmlSourceNote,
        lookup_type='in',
        name='exception_type',
        fk='source')

    note_exception_type_contains = CharFilter(
        lookup_type='icontains',
        name='exception_type')

    note_field = ToManyFilter(
        qs=IatiXmlSourceNote,
        lookup_type='in',
        name='iatixmlsourcenote__field',
        fk='source')

    note_field_contains = CharFilter(
        lookup_type='icontains',
        name='iatixmlsourcenote__field')

    note_count_gte = NumberFilter(
        lookup_type='gte',
        name='note_count')

    date_updated_gte = DateTimeFilter(
        lookup_type='gte',
        name='date_updated')


    class Meta:
        model = IatiXmlSource
