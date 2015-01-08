from rest_framework import serializers
import iati
from api.generics.serializers import DynamicFieldsModelSerializer


class SectorCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = iati.models.SectorCategory
        fields = (
            'code',
        )


class SectorSerializer(DynamicFieldsModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='sector-detail')
    category = SectorCategorySerializer()
    activities = serializers.HyperlinkedIdentityField(view_name='sector-activities')

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
