from rest_framework import serializers
import iati


class SectorDetailSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='sector-detail')

    class Meta:
        model = iati.models.Sector
        fields = ()


class SectorListSerializer(SectorDetailSerializer):
    class Meta:
        model = iati.models.Sector
        fields = ('url', 'code', 'name',)
