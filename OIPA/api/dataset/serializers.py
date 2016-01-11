from rest_framework.serializers import HyperlinkedIdentityField
from rest_framework.serializers import HyperlinkedRelatedField
from rest_framework.serializers import SerializerMethodField
from iati_synchroniser.models import IatiXmlSource
from api.generics.serializers import DynamicFieldsModelSerializer


class DatasetSerializer(DynamicFieldsModelSerializer):

    url = HyperlinkedIdentityField(view_name='datasets:dataset-detail')
    publisher = HyperlinkedRelatedField(
        view_name='publishers:publisher-detail',
        read_only=True)
    type = SerializerMethodField()

    class Meta:
        model = IatiXmlSource
        fields = (
            'url',
            'ref',
            'title',
            'type',
            'publisher',
            'source_url',
            'date_created',
            'date_updated',
            'last_found_in_registry',
            'iati_standard_version')

    def get_type(self,obj):
        return obj.get_type_display()