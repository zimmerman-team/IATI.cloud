from api.generics.serializers import NoCountPaginationSerializer
from django.test import RequestFactory
from rest_framework.pagination import PaginationSerializer
from django.core.paginator import Paginator


class TestNoCount:
    @classmethod
    def setup_class(cls):
        objects = ['String A', 'String B']
        paginator = Paginator(objects, 10)
        cls.page = paginator.page(1)

    def test_count_pagination_serializer(self):
        request = RequestFactory().get('/')
        request.query_params = {}

        serializer = NoCountPaginationSerializer(
            instance=self.page, context={'request': request})

        assert 'count' in serializer.data, \
            'count should be serialized'

    def test_no_count_pagination_serializer(self):
        request = RequestFactory().get('/')
        request.query_params = {'nocount': ''}
        serializer = NoCountPaginationSerializer(
            instance=self.page, context={'request': request})

        assert 'count' not in serializer.data, \
            'count should not be serialized when specified in query_params'
