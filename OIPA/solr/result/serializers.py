from iati.models import Result
from api.activity import serializers
from solr.activity.serializers import ActivitySectorSerializer, RecipientCountrySerializer, \
    ActivityRecipientRegionSerializer


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

    sectors = ActivitySectorSerializer(
        many=True,
        source='activity.activitysector_set',
        read_only=True,
        required=False,
    )
    recipient_countries = RecipientCountrySerializer(
        many=True,
        source='activity.activityrecipientcountry_set',
        read_only=True,
        required=False,
    )
    recipient_regions = ActivityRecipientRegionSerializer(
        many=True,
        source='activity.activityrecipientregion_set',
        read_only=True,
        required=False,
    )

    class Meta:
        model = Result
        fields = (
            'title',
            'description',
            'indicators',
            'type',
            'aggregation_status',
            'document_links',
            'iati_identifier',
            'sectors',
            'recipient_countries',
            'recipient_regions',
            'iati_identifier'
        )
