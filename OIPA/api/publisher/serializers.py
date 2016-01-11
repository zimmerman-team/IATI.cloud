from rest_framework.serializers import HyperlinkedIdentityField
from iati_synchroniser.models import Publisher
from api.generics.serializers import DynamicFieldsModelSerializer
from api.dataset.serializers import DatasetSerializer


class PublisherSerializer(DynamicFieldsModelSerializer):

    url = HyperlinkedIdentityField(view_name='publishers:publisher-detail')
    datasets = DatasetSerializer(
        many=True, 
        source="iatixmlsource_set",
        fields=('url', 'ref', 'title', 'type', 'source_url'))

    class Meta:
        model = Publisher
        fields = (
            'url',
            'org_id',
            'org_abbreviate',
            'org_name',
            'datasets')
