from rest_framework import serializers
import iati


class SectorDetailSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='sector-detail')

    activity_set = serializers.RelatedField(many=True)
    activitysector_set = serializers.RelatedField(many=True)

    class Meta:
        model = iati.models.Sector
        fields = (
            'url',
            'code',
            'name',
            'description',
            'category',

            # Reverse linked data
            'activity_set',
            'activitysector_set',
        )


class SectorListSerializer(SectorDetailSerializer):
    class Meta:
        model = iati.models.Sector
        fields = ('url', 'code', 'name',)
