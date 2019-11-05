from api.activity import serializers
from api.country.serializers import CountrySerializer
from api.region.serializers import BasicRegionSerializer


class ActivitySectorSerializer(serializers.ActivitySectorSerializer):
    sector = serializers.SectorSerializer(fields=('code', 'name'))


class RecipientCountrySerializer(serializers.RecipientCountrySerializer):
    country = CountrySerializer(fields=('code', 'name'))


class ActivityRecipientRegionSerializer(
    serializers.ActivityRecipientRegionSerializer
):
    region = BasicRegionSerializer(
        fields=('code', 'name'),
    )


class LocationSerializer(serializers.LocationSerializer):
    reporting_organisations = serializers.ReportingOrganisationDataSerializer(
        many=True,
        source='activity.reporting_organisations',
        required=False,
        read_only=True,
        fields=[
            'ref',
            'type',
            'secondary_reporter',
            'narratives'
        ]
    )
