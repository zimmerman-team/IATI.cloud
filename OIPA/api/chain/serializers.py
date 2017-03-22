from rest_framework import serializers
from traceability import models as chain_models
from api.generics.serializers import DynamicFieldsModelSerializer
from iati.models import Activity


class SimpleActivitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Activity
        fields = (
            'id',
            'iati_identifier',
        )


class ChainNodeSerializer(DynamicFieldsModelSerializer):
    activity = SimpleActivitySerializer()

    class Meta:
        model = chain_models.Chain
        fields = (
            'chain',
            'activity',
            'activity_identifier',
            'level',
            'bol',
            'eol'
        )


class ChainSerializer(DynamicFieldsModelSerializer):

    links = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name='chains:chain-link-list',
        )
    errors = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name='chains:chain-error-list',
        )
    activities = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name='chains:chain-activity-list',
        )

    class Meta:
        model = chain_models.Chain
        fields = (
            'id',
            'name',
            'last_updated',
            'links',
            'errors',
            'activities'
        )


class ChainLinkRelationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = chain_models.ChainLinkRelation
        fields = (
            'id',
            'chain_link',
            'relation',
            'from_node',
            'related_id'
        )


class ChainLinkSerializer(DynamicFieldsModelSerializer):
    chain = ChainSerializer()
    start_node = ChainNodeSerializer()
    end_node = ChainNodeSerializer()
    relations = ChainLinkRelationSerializer(many=True)

    class Meta:
        model = chain_models.ChainLink
        fields = (
            'id',
            'chain',
            'start_node',
            'end_node',
            'relations'
        )


class ChainNodeErrorSerializer(DynamicFieldsModelSerializer):

    class Meta:
        model = chain_models.ChainNodeError
        fields = (
            'chain',
            'error_type',
            'mentioned_activity_or_org',
            'related_id',
            'warning_level'
        )

