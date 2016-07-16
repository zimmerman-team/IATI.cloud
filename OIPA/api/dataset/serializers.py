from rest_framework.serializers import HyperlinkedIdentityField
from rest_framework.serializers import HyperlinkedRelatedField
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from iati_synchroniser.models import Publisher
from iati_synchroniser.models import IatiXmlSource
from iati_synchroniser.models import IatiXmlSourceNote
from api.generics.serializers import DynamicFieldsModelSerializer
from django.core.urlresolvers import reverse
from iati.models import Activity


class DatasetNoteSerializer(ModelSerializer):
    class Meta:
        model = IatiXmlSourceNote
        fields = ('model', 'iati_identifier', 'exception_type', 'model', 'field', 'message', 'line_number')


class SimplePublisherSerializer(DynamicFieldsModelSerializer):

    url = HyperlinkedIdentityField(view_name='publishers:publisher-detail')

    class Meta:
        model = Publisher
        fields = (
            'id',
            'url',
            'org_id',
            'org_abbreviate',
            'org_name')


class SimpleDatasetSerializer(DynamicFieldsModelSerializer):
    url = HyperlinkedIdentityField(view_name='datasets:dataset-detail')
    publisher = HyperlinkedRelatedField(
        view_name='publishers:publisher-detail',
        read_only=True)
    type = SerializerMethodField()

    class Meta:
        model = IatiXmlSource
        fields = (
            'id',
            'url',
            'ref',
            'title',
            'type',
            'publisher',
            'source_url',
            'iati_standard_version')

    def get_type(self, obj):
        return obj.get_type_display()

class DatasetSerializer(DynamicFieldsModelSerializer):

    url = HyperlinkedIdentityField(view_name='datasets:dataset-detail')
    publisher = SimplePublisherSerializer()
    type = SerializerMethodField()
    activities = SerializerMethodField()
    activity_count = SerializerMethodField()
    notes = HyperlinkedIdentityField(
        view_name='datasets:dataset-notes',)


    DatasetNoteSerializer(many=True, source="iatixmlsourcenote_set")

    class Meta:
        model = IatiXmlSource
        fields = (
            'id',
            'url',
            'ref',
            'title',
            'type',
            'publisher',
            'source_url',
            'activities',
            'activity_count',
            'date_created',
            'date_updated',
            'last_found_in_registry',
            'iati_standard_version',
            'sha1',
            'note_count',
            'notes')

    def get_type(self, obj):
        return obj.get_type_display()

    def get_activities(self, obj):
        request = self.context.get('request')
        url = request.build_absolute_uri(reverse('activities:activity-list'))
        return url + '?xml_source_ref=' + obj.ref

    def get_activity_count(self, obj):
        return Activity.objects.filter(xml_source_ref=obj.ref).count()
