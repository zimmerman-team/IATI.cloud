from rest_framework import serializers

from api.generics.fields import PointField
from api.generics.serializers import DynamicFieldsModelSerializer
from api.codelist.serializers import VocabularySerializer
from api.codelist.serializers import CodelistSerializer
from api.codelist.serializers import CodelistCategorySerializer
from api.codelist.serializers import NarrativeContainerSerializer
from api.codelist.serializers import NarrativeSerializer
from api.activity.serializers import ActivitySerializer

from iati import models as iati_models


class LocationSerializer(DynamicFieldsModelSerializer):
    
    class LocationIdSerializer(serializers.Serializer):
        vocabulary = VocabularySerializer(
            source='location_id_vocabulary')
        code = serializers.CharField(source='location_id_code')


    class PointSerializer(serializers.Serializer):
        pos = PointField(source='point_pos')
        srsName = serializers.CharField(source="point_srs_name")


    class AdministrativeSerializer(serializers.ModelSerializer):
        code = serializers.CharField()
        vocabulary = VocabularySerializer()

        class Meta:
            model = iati_models.LocationAdministrative
            fields = (
                'code',
                'vocabulary',
                'level',
            )

    url = serializers.HyperlinkedIdentityField(view_name='locations:location-detail')
    activity = ActivitySerializer(read_only=True, fields=('id', 'url', 'title'))
    location_reach = CodelistSerializer()
    location_id = LocationIdSerializer(source='*')
    name = NarrativeContainerSerializer(many=True, source="locationname_set")
    description = NarrativeContainerSerializer(many=True, source="locationdescription_set")
    activity_description = NarrativeContainerSerializer(many=True, source="locationactivitydescription_set")
    administrative = AdministrativeSerializer(many=True, source="locationadministrative_set")
    point = PointSerializer(source="*")
    exactness = CodelistSerializer()
    location_class = CodelistSerializer()
    feature_designation = CodelistCategorySerializer()

    class Meta:
        model = iati_models.Location
        fields = (
            'id',
            'url',
            'activity',
            'ref',
            'location_reach',
            'location_id',
            'name',
            'description',
            'activity_description',
            'administrative',
            'point',
            'exactness',
            'location_class',
            'feature_designation',
        )


