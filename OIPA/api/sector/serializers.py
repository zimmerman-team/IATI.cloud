from rest_framework import serializers
import iati
from api.generics.serializers import XMLMetaMixin, DynamicFieldsModelSerializer


class SectorCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = iati.models.SectorCategory
        fields = (
            'code',
        )


class SectorSerializer(XMLMetaMixin, DynamicFieldsModelSerializer):
    xml_meta = {'only': 'code'}

    url = serializers.HyperlinkedIdentityField(view_name='sectors:sector-detail')
    category = SectorCategorySerializer()
    activities = serializers.HyperlinkedIdentityField(
        view_name='sectors:sector-activities')

    class Meta:
        model = iati.models.Sector
        fields = (
            'url',
            'code',
            'name',
            'description',
            'category',
            'activities',
        )
