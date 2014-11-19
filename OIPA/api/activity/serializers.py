from rest_framework import serializers
import iati


class ActivityDetailSerializer(serializers.ModelSerializer):
    title_set = serializers.SlugRelatedField(many=True, slug_field='title')
    url = serializers.HyperlinkedIdentityField(view_name='activity-detail')

    class Meta:
        model = iati.models.Activity
        fields = ()


class ActivityListSerializer(ActivityDetailSerializer):
    class Meta:
        model = iati.models.Activity
        fields = ('id', 'url', 'title_set')
