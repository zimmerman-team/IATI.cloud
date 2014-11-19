from rest_framework import serializers
import iati


class ActivityDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = iati.models.Activity
        fields = ()


class ActivityListSerializer(ActivityDetailSerializer):
    class Meta:
        model = iati.models.Activity
        fields = ('id',)
