from iati.models import Result
from api.activity import serializers


class ResultSerializer(serializers.ResultSerializer):
    document_links = serializers.DocumentLinkSerializer(
        many=True,
        read_only=True,
        source='documentlink_set',
        fields=[
            'format',
            'categories',
            'languages',
            'title',
            'document_date',
            'description'
        ]
    )

    class Meta:
        model = Result
        fields = (
            'title',
            'description',
            'type',
            'aggregation_status',
            'document_links',
            'iati_identifier'
        )
