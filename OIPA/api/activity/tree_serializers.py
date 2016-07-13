from rest_framework import serializers

from iati import models as iati_models
from api.activity.serializers import TitleSerializer

from rest_framework_recursive.fields import RecursiveField



class ActivityProvidingActivitiesSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='activities:activity-detail')
    iati_identifier = serializers.CharField()
    title = TitleSerializer()
    providing_activities = RecursiveField(many=True, source='get_providing_activities')

    class Meta:
        model = iati_models.Activity
        fields = (
            'url',
            'iati_identifier',
            'title',
            'providing_activities')


class ActivityProvidedActivitiesSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='activities:activity-detail')
    iati_identifier = serializers.CharField()
    title = TitleSerializer()
    receiving_activities = RecursiveField(many=True, source='get_provided_activities')

    class Meta:
        model = iati_models.Activity
        fields = (
            'url',
            'iati_identifier',
            'title',
            'receiving_activities')


class ActivityTree(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='activities:activity-detail')
    iati_identifier = serializers.CharField()
    title = TitleSerializer()
    providing_activities = ActivityProvidingActivitiesSerializer(many=True, source='get_providing_activities')
    receiving_activities = ActivityProvidedActivitiesSerializer(many=True, source='get_provided_activities')

    class Meta:
        model = iati_models.Activity
        fields = (
            'url',
            'iati_identifier',
            'title',
            'providing_activities',
            'receiving_activities'
        )


