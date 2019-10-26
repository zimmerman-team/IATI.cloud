from api.activity import serializers


class ActivitySectorSerializer(serializers.ActivitySectorSerializer):
    sector = serializers.SectorSerializer(fields=('code', 'name'))
