from rest_framework import serializers
import geodata
import iati.models
from api.generics.serializers import DynamicFieldsModelSerializer


class RegionVocabularySerializer(serializers.ModelSerializer):
    code = serializers.CharField()

    class Meta:
        model = iati.models.RegionVocabulary
        fields = ('code',)


class BasicRegionSerializer(DynamicFieldsModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='region-detail')
    code = serializers.CharField()
    region_vocabulary = RegionVocabularySerializer()

    class Meta:
        model = geodata.models.Region
        fields = (
            'url',
            'code',
            'name',
            'region_vocabulary'
        )


class RegionSerializer(BasicRegionSerializer):
    child_regions = BasicRegionSerializer(
        many=True, source='region_set', fields=('url', 'code', 'name'))
    parental_region = BasicRegionSerializer(fields=('url', 'code', 'name'))
    countries = serializers.HyperlinkedIdentityField(view_name='region-countries')
    activities = serializers.HyperlinkedIdentityField(view_name='region-activities')

    class Meta:
        model = geodata.models.Region
        fields = (
            'url',
            'code',
            'name',
            'region_vocabulary',
            'parental_region',
            'countries',
            'center_longlat',
            'activities',
            'indicatordata_set',
            'child_regions',
        )
