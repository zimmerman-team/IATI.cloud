from django.db.models import Sum
from django.urls import reverse
from rest_framework.serializers import (
    HyperlinkedIdentityField, SerializerMethodField
)

from api.dataset.serializers import DatasetSerializer
from api.generics.serializers import DynamicFieldsModelSerializer
from iati.models import Activity
from iati_synchroniser.models import Dataset, Publisher


class PublisherSerializer(DynamicFieldsModelSerializer):

    url = HyperlinkedIdentityField(view_name='publishers:publisher-detail')
    datasets = DatasetSerializer(
        many=True,
        source="dataset_set",
        fields=(
            'id',
            'iati_id',
            'url',
            'name',
            'title',
            'filetype',
            'source_url',
            'added_manually',
            'is_parsed',
            'export_in_progress',
            'parse_in_progress'))
    activity_count = SerializerMethodField()
    note_count = SerializerMethodField()
    activities = SerializerMethodField()

    class Meta:
        model = Publisher
        fields = (
            'id',
            'url',
            'iati_id',
            'publisher_iati_id',
            'display_name',
            'name',
            'organisation',
            'activities',
            'activity_count',
            'note_count',
            'datasets',)

    def get_activities(self, obj):
        request = self.context.get('request')
        url = request.build_absolute_uri(reverse('activities:activity-list'))
        return (url
                + '?reporting_organisation_identifier='
                + obj.publisher_iati_id)

    def get_activity_count(self, obj):
        return Activity.objects.filter(
            reporting_organisations__normalized_ref=obj.publisher_iati_id
        ).count()

    def get_note_count(self, obj):
        sum_queryset = Dataset.objects.filter(
            publisher=obj.id
        ).aggregate(Sum('note_count'))
        return sum_queryset.get('note_count__sum')
