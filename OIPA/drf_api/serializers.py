from rest_framework import serializers
import iati


class ActivityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = iati.models.Activity
        fields = ('id',)
