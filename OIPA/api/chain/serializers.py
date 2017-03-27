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
        model = chain_models.ChainNode
        fields = (
            'id',
            'chain',
            'activity',
            'activity_oipa_id',
            'activity_iati_id',
            'tier',
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
    transactions = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name='chains:chain-transaction-list',
        )
    nodes = serializers.HyperlinkedIdentityField(
        read_only=True,
        view_name='chains:chain-node-list',
        )

    url = serializers.HyperlinkedIdentityField(view_name='chains:chain-detail', read_only=True)

    class Meta:
        model = chain_models.Chain
        fields = (
            'id',
            'url',
            'name',
            'last_updated',
            'links',
            'errors',
            'activities',
            'transactions',
            'nodes'
        )


class ChainLinkRelationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = chain_models.ChainLinkRelation
        fields = (
            'relation',
            'from_node',
            'related_id'
        )


class ChainLinkSerializer(DynamicFieldsModelSerializer):
    start_node = ChainNodeSerializer(fields=('id', 'activity_oipa_id', 'activity_iati_id', 'tier', 'eol', 'bol'))
    end_node = ChainNodeSerializer(fields=('id', 'activity_oipa_id', 'activity_iati_id', 'tier', 'eol', 'bol'))
    relations = ChainLinkRelationSerializer(many=True)

    class Meta:
        model = chain_models.ChainLink
        fields = (
            'id',
            'start_node',
            'end_node',
            'relations'
        )


class ChainNodeErrorSerializer(DynamicFieldsModelSerializer):

    class Meta:
        model = chain_models.ChainNodeError
        fields = (
            'chain_node',
            'error_type',
            'mentioned_activity_or_org',
            'related_id',
            'warning_level'
        )

