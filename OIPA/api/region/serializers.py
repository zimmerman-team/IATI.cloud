from rest_framework import serializers
import geodata


class RegionDetailSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='region-detail')

    class Meta:
        model = geodata.models.Region
        fields = ()


class RegionListSerializer(RegionDetailSerializer):
    class Meta:
        model = geodata.models.Region
        fields = ('url', 'code', 'name')
