from rest_framework.generics import RetrieveAPIView, GenericAPIView, ListAPIView
from api.generics.serializers import DynamicFieldsModelSerializer
from django.db.models.fields.related import ForeignKey, OneToOneField

class DynamicView(GenericAPIView):
            
    # foreign / one-to-one fields that can be used with select_related()
    select_related_fields = []
    serializer_fields = []
    field_source_mapping = {}

    def __init__(self, *args, **kwargs):
        """
        Extract prefetches and default fields from Meta
        """
        # TODO: move this to a meta class, to evaluate once when defining the class
        # TODO: This is not efficient - 2016-01-20

        serializer_class = self.get_serializer_class() 
        serializer = serializer_class() # need an instance to extract fields
        model = serializer_class.Meta.model

        assert issubclass(serializer_class, DynamicFieldsModelSerializer), (
            "serializer class must be an instance of DynamicFieldsModelSerializer "
            "instead got %s") % (serializer_class.__name__,)

        self.serializer_fields = serializer.fields.keys()

        self.select_related_fields = [ field.name for field in model._meta.fields \
                if isinstance(field, (ForeignKey, OneToOneField)) ]

        self.field_source_mapping = { field.field_name: field.source for field in serializer.fields.values() \
                if isinstance(field, (ForeignKey, OneToOneField)) }

    def _get_query_fields(self):
        request_fields = self.request.query_params.get('fields')

        if request_fields:
            return request_fields.split(',')
        else:
            return getattr(self, 'fields', ())

    def filter_queryset(self, queryset, *args, **kwargs):
        """
        Prefetches based on 'fields' GET arg
        """

        fields = self._get_query_fields(*args, **kwargs)
        if not fields: fields = self.serializer_fields

        select_related_fields = list(set(self.select_related_fields) & set(fields))

        if select_related_fields:
            queryset = queryset.select_related(*select_related_fields)

        for field in fields:
            # TODO: Hook this up in the view - 2016-01-15
            if hasattr(queryset, 'prefetch_%s' % field):
                queryset = getattr(queryset, 'prefetch_%s' % field)()

        queryset = super(DynamicView, self).filter_queryset(queryset, *args, **kwargs)

        return queryset


    def get_serializer(self, *args, **kwargs):
        """
        Apply 'fields' to dynamic fields serializer
        """
        fields = self._get_query_fields()
        kwargs['context'] = self.get_serializer_context()
        return super(DynamicView, self).get_serializer(fields=fields, *args, **kwargs)

class DynamicListView(DynamicView, ListAPIView):
    """
    List view with dynamic properties
    """

class DynamicDetailView(DynamicView, RetrieveAPIView):
    """
    List view with dynamic properties
    """
