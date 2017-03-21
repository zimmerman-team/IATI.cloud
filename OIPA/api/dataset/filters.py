from api.generics.filters import CommaSeparatedCharFilter, ToManyFilter
from iati_synchroniser.models import Dataset, DatasetNote
from django_filters import FilterSet, CharFilter, NumberFilter, DateTimeFilter


class DatasetFilter(FilterSet):
    """
    Filter countries list
    """

    id = CharFilter(
        lookup_expr='exact',
        name='id')

    name = CharFilter(
        lookup_expr='icontains',
        name='name')

    title = CharFilter(
        lookup_expr='icontains',
        name='title')

    filetype = CommaSeparatedCharFilter(
        lookup_expr='in',
        name='filetype')

    publisher_id = CharFilter(
        lookup_expr='exact',
        name='publisher__id')

    publisher_name = CharFilter(
        lookup_expr='icontains',
        name='publisher__publisher_iati_id')

    publisher_title = CharFilter(
        lookup_expr='icontains',
        name='publisher__title')

    note_exception_type = ToManyFilter(
        qs=DatasetNote,
        lookup_expr='in',
        name='exception_type',
        fk='source')

    note_exception_type_contains = ToManyFilter(
        qs=DatasetNote,
        lookup_expr='icontains',
        name='exception_type',
        fk='source')

    note_model = ToManyFilter(
        qs=DatasetNote,
        lookup_expr='in',
        name='model',
        fk='source')

    note_model_contains = ToManyFilter(
        qs=DatasetNote,
        lookup_expr='icontains',
        name='model',
        fk='source')

    note_field = ToManyFilter(
        qs=DatasetNote,
        lookup_expr='in',
        name='field',
        fk='source')

    note_field_contains = ToManyFilter(
        qs=DatasetNote,
        lookup_expr='icontains',
        name='field',
        fk='source')

    note_message = ToManyFilter(
        qs=DatasetNote,
        lookup_expr='in',
        name='field',
        fk='source')

    note_message_contains = ToManyFilter(
        qs=DatasetNote,
        lookup_expr='icontains',
        name='field',
        fk='source')

    note_count_gte = NumberFilter(
        lookup_expr='gte',
        name='note_count')

    metadata_modified_gte = DateTimeFilter(
        lookup_expr='gte',
        name='metadata_modified')


    class Meta:
        model = Dataset
        fields = '__all__'
