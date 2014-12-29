from rest_framework import serializers
import geodata
import iati.models
from api.generics.serializers import DynamicFieldsModelSerializer
from api.fields import GeometryField


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
    location = GeometryField(source='center_longlat')

    class Meta:
        model = geodata.models.Region
        fields = (
            'url',
            'code',
            'name',
            'region_vocabulary',
            'parental_region',
            'countries',
            'activities',
            'location',
            'child_regions',
        )
