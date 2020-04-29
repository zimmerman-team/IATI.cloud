import copy

from django.db.models.fields.related import ForeignKey, OneToOneField
from rest_framework import mixins
from rest_framework.generics import (
    GenericAPIView, ListAPIView, ListCreateAPIView, RetrieveAPIView,
    RetrieveUpdateDestroyAPIView
)

from api.generics.serializers import (
    DynamicFieldsModelSerializer, DynamicFieldsSerializer
)


class DynamicView(GenericAPIView):

    # foreign / one-to-one fields that can be used with select_related()
    select_related_fields = []
    serializer_fields = []
    field_source_mapping = {}
    fields = ()
    selectable_fields = ()

    def __init__(self, *args, **kwargs):
        """
        Extract prefetches and default fields from Meta
        """
        # TODO: move this to a meta class, to evaluate once when defining the
        # class
        # TODO: This is not efficient - 2016-01-20

        serializer_class = self.get_serializer_class()
        serializer = serializer_class()  # need an instance to extract fields
        model = serializer_class.Meta.model

        assert issubclass(
            serializer_class, DynamicFieldsModelSerializer
        ) or issubclass(serializer_class, DynamicFieldsSerializer), (
            "serializer class must be an instance of \
             DynamicFieldsModelSerializer " "instead got %s"
        ) % (serializer_class.__name__,)

        self.serializer_fields = serializer.fields.keys()

        self.select_related_fields = [
            field.name for field in model._meta.fields
            if isinstance(field, (ForeignKey, OneToOneField))
        ]

        self.field_source_mapping = {
            field.field_name: field.source
            for field in serializer.fields.values()
            if isinstance(
                field, (ForeignKey, OneToOneField)
            )
        }

    def _get_query_fields(self):
        if not self.request:
            return ()

        request_fields = self.request.query_params.get('fields')

        # if requested query fields is set to `all` we will return all
        # serializer fields defined in serializer class. Here we assign
        # `self.fields = ()` so that it will be assigned all serializer
        # fields in `filter_queryset` method.
        if request_fields and request_fields == 'all':
            self.fields = ()
            self.selectable_fields = (self.selectable_fields + tuple(
                self.serializer_fields))
        elif request_fields:
            for request_field in request_fields.split(','):
                if request_field not in list(self.fields):
                    # put selectable fields together with required fields
                    # defined in the class
                    self.fields = self.fields + (request_field,)
                    # just in case if you want to know which of fields
                    # we get as selectable field
                    self.selectable_fields = self.selectable_fields+(request_field,)  # NOQA: E501

            # Some bugs if request fields has 'aggregations'
            # So we need to remove it from request fields.
            # And assign a tuple fields without aggregations
            fields = list(self.fields)
            try:
                fields.remove('aggregations')
            except ValueError:
                pass
            # Assign it again
            self.fields = tuple(fields)

        return getattr(self, 'fields', ())

    def filter_queryset(self, queryset, *args, **kwargs):
        """
        Prefetches based on 'fields' GET arg
        """
        filter_fields = copy.deepcopy(self.request.query_params)

        if 'fields' in filter_fields:
            filter_fields.pop('fields')
        if 'format' in filter_fields:
            filter_fields.pop('format')
        if 'page' in filter_fields:
            filter_fields.pop('page')
        if 'page_size' in filter_fields:
            filter_fields.pop('page_size')
        if 'ordering' in filter_fields:
            filter_fields.pop('ordering')
        if 'q'in filter_fields:
            filter_fields.pop('q')
        if 'q_fields' in filter_fields:
            filter_fields.pop('q_fields')

        for filter_field in filter_fields:
            found = False
            try:
                declared_filters = self.filter_class.declared_filters

                for key in declared_filters:
                    if filter_field == key:
                        found = True
                if found is False:
                    # make error in the code to fail
                    # if input wrong filter name.
                    setattr(self, 'filter_class', 'No Filter Class')
                    break
            except AttributeError:
                pass
        fields = self._get_query_fields(*args, **kwargs)
        if not fields:
            fields = self.serializer_fields

        select_related_fields = list(set(
            self.select_related_fields
        ) & set(fields))

        if select_related_fields:
            queryset = queryset.select_related(*select_related_fields)

        for field in fields:
            # TODO: Hook this up in the view - 2016-01-15
            if hasattr(queryset, 'prefetch_%s' % field):
                queryset = getattr(queryset, 'prefetch_%s' % field)()

        queryset = super(DynamicView, self).filter_queryset(
            queryset, *args, **kwargs
        )

        return queryset

    def get_serializer(self, *args, **kwargs):
        """
        Apply 'fields' to dynamic fields serializer
        """
        fields = self._get_query_fields()
        kwargs['context'] = self.get_serializer_context()
        return super(DynamicView, self).get_serializer(
            fields=fields, *args, **kwargs
        )


class DynamicListView(DynamicView, ListAPIView):
    """
    List view with dynamic properties
    """


class DynamicDetailView(DynamicView, RetrieveAPIView):
    """
    List view with dynamic properties
    """


class DynamicListCRUDView(DynamicView, ListCreateAPIView):
    """
    List view with dynamic properties
    """


class DynamicDetailCRUDView(DynamicView, RetrieveUpdateDestroyAPIView):
    """
    List view with dynamic properties
    """


class SaveAllSerializer(mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        mixins.CreateModelMixin,
                        GenericAPIView):

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
