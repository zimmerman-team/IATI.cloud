from rest_framework import serializers
from api.generics.serializers import DynamicFieldsModelSerializer
from api.fields import JSONField
from api.activity.aggregation import AggregationsSerializer
from api.activity.serializers import *
import iati


class ActivityPolicyMarkerSerializer(serializers.RelatedField,DynamicFieldsModelSerializer):
    class PolicyMarkerSerializer(serializers.ModelSerializer):
        code = serializers.CharField()

        class Meta:
            model = iati.models.PolicyMarker
            fields = ('code',)

    class PolicySignificanceSerializer(serializers.ModelSerializer):
        code = serializers.CharField()

        class Meta:
            model = iati.models.PolicySignificance
            fields = ('code',)

    # class VocabularySerializer(serializers.ModelSerializer):
    #     code = serializers.CharField()

    #     class Meta:
    #         model = iati.models.Vocabulary
    #         fields = ('code',)

    # vocabulary = VocabularySerializer(serializers.ModelSerializer)
    code = PolicyMarkerSerializer(source='policy_marker')
    significance = PolicySignificanceSerializer(source='policy_significance')
    narative = serializers.CharField(source='alt_policy_marker')

    activity = ActivitySerializer()

    class Meta:
        model = iati.models.ActivityPolicyMarker
        fields = (
            'vocabulary',
            'code',
            'significance',
            'narative',
            'activity')
        
       


class PolicyMarkerSerializer(DynamicFieldsModelSerializer):
    
    #activity_policy_marker_related = serializers.StringRelatedField(many=True)
    #aggregations = AggregationsSerializer(source='activity_policy_marker_related', fields=())
    policy_marker_related = ActivityPolicyMarkerSerializer( read_only=`True`,many=True)
    
    class Meta:
        model = iati.models.PolicyMarker
        fields = (
            'code',
            'name',
            'description',
            'vocabulary',
            'policy_marker_related',
            


        )

