from rest_framework import generics
import iati
from api.activity import serializers
from rest_framework import serializers as drf_serializers
from rest_framework import pagination as drf_pagination


class ActivityList(generics.ListAPIView):
    queryset = iati.models.Activity.objects.all()
    serializer_class = serializers.ActivitySerializer

    def get_pagination_serializer(self, page):
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

        fields = ['url', 'id', 'title_set']
        request_fields = self.request.QUERY_PARAMS.get('fields', None)

        if request_fields is not None:
            fields.extend(request_fields.split(','))

        return pagination_serializer_class(instance=page, context=context, fields=fields)


class ActivityDetail(generics.RetrieveAPIView):
    queryset = iati.models.Activity.objects.all()
    serializer_class = serializers.ActivitySerializer

    def get_serializer(self, instance=None, data=None, many=False, partial=False):
        serializer_class = self.get_serializer_class()
        context = self.get_serializer_context()
        fields = serializers.ActivitySerializer.Meta.fields

        request_fields = self.request.QUERY_PARAMS.get('fields', None)

        if request_fields is not None:
            fields = request_fields.split(',')

        return serializer_class(instance, data=data, many=many, partial=partial, context=context, fields=fields)


class ActivitySectors(generics.ListAPIView):
    serializer_class = serializers.ActivitySectorSerializer


    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return iati.models.Activity(pk=pk).activitysector_set.all()


class ActivityParticipatingOrganisations(generics.ListAPIView):
    serializer_class = serializers.ParticipatingOrganisationSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return iati.models.Activity(pk=pk).participating_organisations.all()


class ActivityRecipientCountry(generics.ListAPIView):
    serializer_class = serializers.RecipientCountrySerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return iati.models.Activity(pk=pk).activityrecipientcountry_set.all()
