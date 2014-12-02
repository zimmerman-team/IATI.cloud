from rest_framework import serializers
import geodata


class RegionDetailSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='region-detail')

    activity_set = serializers.RelatedField(many=True, read_only=True)
    activityrecipientregion_set = serializers.RelatedField(
        many=True, read_only=True)
    country_set = serializers.RelatedField(many=True, read_only=True)
    indicatordata_set = serializers.RelatedField(many=True, read_only=True)
    region_set = serializers.RelatedField(many=True, read_only=True)
    un_region = serializers.RelatedField(many=True, read_only=True)
    unesco_region = serializers.RelatedField(many=True, read_only=True)

    class Meta:
        model = geodata.models.Region
        fields = (
            'url',
            'code',
            'name',
            'region_vocabulary',
            'parental_region',
            'center_longlat',

            # Reverse linked data
            'activity_set',
            'activityrecipientregion_set',
            'country_set',
            'indicatordata_set',
            'region_set',
            'un_region',
            'unesco_region',
        )


class RegionListSerializer(RegionDetailSerializer):
    class Meta:
        model = geodata.models.Region
