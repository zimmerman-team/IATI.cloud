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
    url = serializers.HyperlinkedIdentityField(
        view_name='regions:region-detail')
    code = serializers.CharField()
    region_vocabulary = RegionVocabularySerializer(required=False)

    class Meta:
        model = geodata.models.Region
        fields = (
            'url',
            'code',
            'name',
            'region_vocabulary'
        )


class RegionSerializer(DynamicFieldsModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='regions:region-detail')
    child_regions = BasicRegionSerializer(
        many=True, source='region_set', fields=('url', 'code', 'name'))
    parental_region = BasicRegionSerializer(fields=('url', 'code', 'name'))
    # location = GeometryField(source='center_longlat')

    class Meta:
        model = geodata.models.Region
        fields = (
            'url',
            'pk',
            'code',
            'name',
            'region_vocabulary',
            'parental_region',
            # 'location',
            'child_regions',
        )
