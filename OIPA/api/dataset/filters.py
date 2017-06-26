from api.generics.filters import CommaSeparatedCharFilter, ToManyFilter
from iati_synchroniser.models import Dataset, DatasetNote
from django_filters import Filter, FilterSet, CharFilter, NumberFilter, DateTimeFilter
from django.db.models import Q


class SearchQueryFilter(Filter):

    def filter(self, qs, value):
        if value:
            return qs.filter(
                Q(publisher__publisher_iati_id__icontains=value) | Q(title__icontains=value) | Q(name__icontains=value)
            )
        return qs


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
        fk='dataset')

    note_model_contains = ToManyFilter(
        qs=DatasetNote,
        lookup_expr='icontains',
        name='model',
        fk='dataset')

    note_field = ToManyFilter(
        qs=DatasetNote,
        lookup_expr='in',
        name='field',
        fk='dataset')

    note_field_contains = ToManyFilter(
        qs=DatasetNote,
        lookup_expr='icontains',
        name='field',
        fk='dataset')

    note_message = ToManyFilter(
        qs=DatasetNote,
        lookup_expr='in',
        name='message',
        fk='dataset')

    note_message_contains = ToManyFilter(
        qs=DatasetNote,
        lookup_expr='icontains',
        name='message',
        fk='dataset')

    note_count_gte = NumberFilter(
        lookup_expr='gte',
        name='note_count')

    metadata_modified_gte = DateTimeFilter(
        lookup_expr='gte',
        name='metadata_modified')

    q = SearchQueryFilter()


    class Meta:
        model = Dataset
        fields = '__all__'



