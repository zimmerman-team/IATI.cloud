from rest_framework_extensions.key_constructor.constructors \
    import DefaultKeyConstructor
from rest_framework_extensions.key_constructor.bits import QueryParamsKeyBit


class QueryParamsKeyConstructor(DefaultKeyConstructor):
    """
    Example:
    class ProductViewSet(CacheResponseMixin, mixins.ListModelMixin,
        mixins.RetrieveModelMixin, viewsets.GenericViewSet):
        queryset = Product.objects.filter(withdrawn=False)
        serializer_class = ProductSerializer
        pagination_class = LargeResultsSetPagination
        list_cache_key_func = QueryParamsKeyConstructor()
    """
    all_query_params = QueryParamsKeyBit()

