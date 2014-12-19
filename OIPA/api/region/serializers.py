from rest_framework import serializers
import geodata
from api.generics.serializers import DynamicFieldsModelSerializer


class RegionSerializer(DynamicFieldsModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='region-detail')
    code = serializers.CharField()

    class Meta:
        model = geodata.models.Region
        fields = (
            'url',
            'code',
            'name',
            'region_vocabulary',
            'parental_region',
            'center_longlat',

            # Reverse linked data
            'activity_set',
            'activityrecipientregion_set',
            'country_set',
            'indicatordata_set',
            'region_set',
            'un_region',
            'unesco_region',
        )
