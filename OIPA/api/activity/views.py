from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from iati.models import Activity
from api.activity import serializers
from api.generics.filters import BasicFilterBackend
from api.generics.filters import SearchFilter
from rest_framework.filters import OrderingFilter
from api.activity import filters
from api.activity.aggregation import AggregationsSerializer


class ActivityList(ListAPIView):
    queryset = Activity.objects.all()
    filter_backends = (SearchFilter, BasicFilterBackend, OrderingFilter,)
    filter_class = filters.ActivityFilter
    serializer_class = serializers.ActivitySerializer
    fields = ('url', 'id', 'title', 'total_budget')

    def get_pagination_serializer(self, page):
        class SerializerClass(self.pagination_serializer_class):
            aggregations = AggregationsSerializer(
                source='paginator.object_list',
                query_field='aggregations',
                fields=()
            )

            class Meta:
                object_serializer_class = self.get_serializer_class()

        pagination_serializer_class = SerializerClass
        context = self.get_serializer_context()
        return pagination_serializer_class(instance=page, context=context)


class ActivityDetail(RetrieveAPIView):
    queryset = Activity.objects.all()
    serializer_class = serializers.ActivitySerializer


class ActivitySectors(ListAPIView):
    serializer_class = serializers.ActivitySectorSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Activity(pk=pk).activitysector_set.all()


class ActivityParticipatingOrganisations(ListAPIView):
    serializer_class = serializers.ParticipatingOrganisationSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Activity(pk=pk).participating_organisations.all()


class ActivityRecipientCountries(ListAPIView):
    serializer_class = serializers.RecipientCountrySerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Activity(pk=pk).activityrecipientcountry_set.all()


class ActivityRecipientRegions(ListAPIView):
    serializer_class = serializers.ActivityRecipientRegionSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Activity(pk=pk).activityrecipientregion_set.all()
