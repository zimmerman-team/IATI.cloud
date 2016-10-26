from rest_framework.serializers import HyperlinkedIdentityField
from rest_framework.serializers import HyperlinkedRelatedField
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from iati_synchroniser.models import Publisher
from iati_synchroniser.models import Dataset
from iati_synchroniser.models import DatasetNote
from api.generics.serializers import DynamicFieldsModelSerializer
from django.core.urlresolvers import reverse
from iati.models import Activity


class DatasetNoteSerializer(ModelSerializer):
    class Meta:
        model = DatasetNote
        fields = ('model', 'iati_identifier', 'exception_type', 'model', 'field', 'message', 'line_number')


class SimplePublisherSerializer(DynamicFieldsModelSerializer):

    url = HyperlinkedIdentityField(view_name='publishers:publisher-detail')

    class Meta:
        model = Publisher
        fields = (
            'id',
            'url',
            'publisher_iati_id',
            'display_name',
            'name')


class SimpleDatasetSerializer(DynamicFieldsModelSerializer):
    url = HyperlinkedIdentityField(view_name='datasets:dataset-detail')
    publisher = HyperlinkedRelatedField(
        view_name='publishers:publisher-detail',
        read_only=True)
    type = SerializerMethodField()

    class Meta:
        model = Dataset
        fields = (
            'id',
            'url',
            'name',
            'title',
            'filetype',
            'publisher',
            'source_url',
            'iati_version')

    def get_type(self, obj):
        return obj.get_filetype_display()

class DatasetSerializer(DynamicFieldsModelSerializer):

    url = HyperlinkedIdentityField(view_name='datasets:dataset-detail')
    publisher = SimplePublisherSerializer()
    filetype = SerializerMethodField()
    activities = SerializerMethodField()
    activity_count = SerializerMethodField()
    notes = HyperlinkedIdentityField(
        view_name='datasets:dataset-notes',)


    DatasetNoteSerializer(many=True, source="datasetnote_set")

    class Meta:
        model = Dataset
        fields = (
            'id',
            'url',
            'name',
            'title',
            'filetype',
            'publisher',
            'source_url',
            'activities',
            'activity_count',
            'date_created',
            'date_updated',
            'last_found_in_registry',
            'iati_version',
            'sha1',
            'note_count',
            'notes')

    def get_filetype(self, obj):
        return obj.get_filetype_display()

    def get_activities(self, obj):
        request = self.context.get('request')
        url = request.build_absolute_uri(reverse('activities:activity-list'))
        return url + '?xml_source_ref=' + obj.name

    def get_activity_count(self, obj):
        return Activity.objects.filter(xml_source_ref=obj.name).count()
