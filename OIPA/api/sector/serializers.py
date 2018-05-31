from rest_framework import serializers

import iati
from api.generics.serializers import DynamicFieldsSerializer


class SectorCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = iati.models.SectorCategory
        fields = (
            'code',
        )


class SectorSerializer(DynamicFieldsSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='sectors:sector-detail',
        read_only=True
    )
    category = SectorCategorySerializer(read_only=True)

    code = serializers.CharField()
    name = serializers.CharField()

    class Meta:
        model = iati.models.Sector
        fields = (
            'url',
            'code',
            'name',
            'description',
            'category',
        )
