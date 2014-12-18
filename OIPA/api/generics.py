from rest_framework import generics
from rest_framework.pagination import DefaultObjectSerializer
from rest_framework.serializers import ListSerializer


def get_dynamic_pagination_serializer(self, page):
    class SerializerClass(self.pagination_serializer_class):
        class Meta:
            object_serializer_class = self.get_serializer_class()

        def __init__(self, *args, **kwargs):
            # remove 'fields' before super otherwise validation will fail
            fields_arg = kwargs.pop('fields', None)

            super(SerializerClass, self).__init__(*args, **kwargs)
            results_field = self.results_field

            try:
                object_serializer = self.Meta.object_serializer_class
            except AttributeError:
                object_serializer = DefaultObjectSerializer

            self.fields[results_field] = ListSerializer(
                child=object_serializer(fields=fields_arg),
                source='object_list'
            )

    pagination_serializer_class = SerializerClass
    context = self.get_serializer_context()

    request_fields = self.request.QUERY_PARAMS.get('fields', None)

    if request_fields is not None:
        self.fields = request_fields.split(',')

    return pagination_serializer_class(
        instance=page, context=context, fields=self.fields)


def get_dynamic_serializer(
        self, *args, **kwargs):
    serializer_class = self.get_serializer_class()
    kwargs['context'] = self.get_serializer_context()

    request_fields = self.request.QUERY_PARAMS.get('fields', None)
    if request_fields is not None:
        kwargs['fields'] = request_fields.split(',')

    return serializer_class(*args, **kwargs)


class DynamicListAPIView(generics.ListAPIView):
    get_pagination_serializer = get_dynamic_pagination_serializer


class DynamicRetrieveAPIView(generics.RetrieveAPIView):
    get_serializer = get_dynamic_serializer
