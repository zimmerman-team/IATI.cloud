from rest_framework import generics
from rest_framework import pagination as drf_pagination
from rest_framework import serializers as drf_serializers


def get_dynamic_pagination_serializer(self, page):
    # get serializer never gets called because ListAPIView calls paginator.
    # paginator class def get_serializer_class but not get_serializer
    # overwrite pagination serializer since it's the method that does get called
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
                object_serializer = drf_pagination.DefaultObjectSerializer

            self.fields[results_field] = drf_serializers.ListSerializer(
                child=object_serializer(args, kwargs, fields=fields_arg),
                source='object_list'
            )

    pagination_serializer_class = SerializerClass
    context = self.get_serializer_context()

    request_fields = self.request.QUERY_PARAMS.get('fields', None)

    if request_fields is not None:
        self.fields = []
        self.fields.extend(request_fields.split(','))

    return pagination_serializer_class(
        instance=page, context=context, fields=self.fields)


class DynamicListAPIView(generics.ListAPIView):
    get_pagination_serializer = get_dynamic_pagination_serializer
