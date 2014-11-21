from rest_framework import serializers
import geodata


class CityDetailSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='city-detail')

    indicatordata_set = serializers.RelatedField(many=True)
    capital_city = serializers.RelatedField(many=True)

    class Meta:
        model = geodata.models.City
        fields = (
            'url',
            'id',
            'geoname_id',
            'name',
            'country',
            'location',
            'ascii_name',
            'alt_name',
            'namepar',

            # Reverse linked data
            'indicatordata_set',
            'capital_city',
        )


class CityListSerializer(CityDetailSerializer):
    class Meta:
        model = geodata.models.City
        fields = ('url', 'id', 'name')
