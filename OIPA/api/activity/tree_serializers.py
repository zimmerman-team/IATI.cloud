from rest_framework import serializers

from iati import models as iati_models
from api.generics.serializers import DynamicFieldsSerializer
from api.generics.serializers import DynamicFieldsModelSerializer
from api.generics.fields import PointField
from api.sector.serializers import SectorSerializer
from api.region.serializers import RegionSerializer
from api.country.serializers import CountrySerializer
from api.activity.filters import RelatedActivityFilter

from api.codelist.serializers import VocabularySerializer
from api.codelist.serializers import CodelistSerializer
from api.codelist.serializers import NarrativeContainerSerializer
from api.codelist.serializers import NarrativeSerializer
from api.codelist.serializers import CodelistCategorySerializer
from rest_framework_recursive.fields import RecursiveField


class ActivitySer(serializers.ModelSerializer):
    iati_identifier = serializers.CharField()

    class Meta:
        model = iati_models.Activity
        fields = (
            'iati_identifier',
        )


class ActivityProvidingActivitiesSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='activities:activity-detail')
    iati_identifier = serializers.CharField()
    providing_activities = RecursiveField(many=True, source='get_providing_activities')

    class Meta:
        model = iati_models.Activity
        fields = (
            'url',
            'iati_identifier',
            'providing_activities')


class ActivityProvidedActivitiesSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='activities:activity-detail')
    iati_identifier = serializers.CharField()
    provided_activities = RecursiveField(many=True, source='get_provided_activities')

    class Meta:
        model = iati_models.Activity
        fields = (
            'url',
            'iati_identifier',
            'provided_activities')


