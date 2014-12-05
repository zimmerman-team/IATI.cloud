from rest_framework import generics
import iati
from api.activity import serializers
from api.generics import DynamicListAPIView


class ActivityList(DynamicListAPIView):
    queryset = iati.models.Activity.objects.all()
    serializer_class = serializers.ActivitySerializer
    fields = ['url', 'id', 'title_set']


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
