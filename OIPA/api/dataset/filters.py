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

    note_model = ToManyFilter(
        qs=IatiXmlSourceNote,
        lookup_type='in',
        name='model',
        fk='source')

    note_model_contains = CharFilter(
        lookup_type='icontains',
        name='model')

    note_field = ToManyFilter(
        qs=IatiXmlSourceNote,
        lookup_type='in',
        name='field',
        fk='source')

    note_field_contains = CharFilter(
        lookup_type='icontains',
        name='field')

    note_message = ToManyFilter(
        qs=IatiXmlSourceNote,
        lookup_type='in',
        name='field',
        fk='source')

    note_message_contains = CharFilter(
        lookup_type='icontains',
        name='field')

    note_count_gte = NumberFilter(
        lookup_type='gte',
        name='note_count')

    date_updated_gte = DateTimeFilter(
        lookup_type='gte',
        name='date_updated')


    class Meta:
        model = IatiXmlSource
