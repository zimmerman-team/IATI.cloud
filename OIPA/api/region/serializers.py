from rest_framework import serializers
import geodata


class RegionDetailSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='region-detail')

    activity_set = serializers.RelatedField(many=True)
    activityrecipientregion_set = serializers.RelatedField(many=True)
    country_set = serializers.RelatedField(many=True)
    indicatordata_set = serializers.RelatedField(many=True)
    region_set = serializers.RelatedField(many=True)
    un_region = serializers.RelatedField(many=True)
    unesco_region = serializers.RelatedField(many=True)

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
        fields = ('url', 'code', 'name')
