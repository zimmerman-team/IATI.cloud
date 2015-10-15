from rest_framework.generics import RetrieveAPIView, GenericAPIView, ListAPIView
from api.generics.serializers import DynamicFieldsModelSerializer

class DynamicView(GenericAPIView):
            
    fields = ()
    prefetches = {}

    def __init__(self):
        """
        Extract prefetches and default fields from Meta
        """

        serializer = self.get_serializer_class()
        fields = getattr(self, 'fields')

        assert issubclass(serializer, DynamicFieldsModelSerializer), \
            """
            serializer class must be an instance of DynamicFieldsModelSerializer
            """

        # print(serializer.fields.keys())

        # if fields:
        #     for field in fields:
        #         assert field in serializer.fields, ( 
        #             "field %s is not in %s" 
        #         ) % ( field, serializer.__class.__name)


        # TODO: apply select_related based on fields -> requires generating list of foreignkeys and OneToOne relations of model on serializer
        # serializer_model = self

        # self.prefetches = getattr(self, 'prefetches', {})
        # for prefetch in self.prefetches.values():
        #     assert isinstance(prefetch, Prefetch), (
        #         "prefetches should use the Prefetch object"
        #     )

    def _get_query_fields(self):
        request_fields = self.request.query_params.get('fields')

        if request_fields:
            return request_fields.split(',')
        else:
            return getattr(self, 'fields', ())

    def get_queryset(self, *args, **kwargs):
        """
        Prefetches based on 'fields' GET arg
        """
        queryset = super(DynamicView, self).get_queryset()

        fields = self._get_query_fields(*args, **kwargs)

        # select_related_fields = [ v for v in self._related_fields if v in request_fields]
        # queryset = queryset.select_related(*select_related_fields)
        queryset = queryset.select_related()

        prefetch_fields = [ v for k,v in self.prefetches.items() if k in fields ]
        print(fields)
        for field in fields:
            if hasattr(queryset, 'prefetch_%s' % field):
                queryset = getattr(queryset, 'prefetch_%s' % field)()

        # print(self.prefetches.items())
        # print(fields)
        # print(prefetch_fields)
        # queryset = queryset.prefetch_related(*prefetch_fields)

        return queryset


    def get_serializer(self, *args, **kwargs):
        """
        Apply 'fields' to dynamic fields serializer
        """
        fields = self._get_query_fields()
        return super(DynamicView, self).get_serializer(fields=fields, *args, **kwargs)

class DynamicListView(DynamicView, ListAPIView):
    """
    List view with dynamic properties
    """

class DynamicDetailView(DynamicView, RetrieveAPIView):
    """
    List view with dynamic properties
    """

