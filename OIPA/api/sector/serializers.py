from rest_framework import serializers

from api.generics.serializers import DynamicFieldsSerializer
from iati_codelists.models import Sector, SectorCategory


class SectorCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SectorCategory
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
        model = Sector
        fields = (
            'url',
            'code',
            'name',
            'description',
            'category',
        )
