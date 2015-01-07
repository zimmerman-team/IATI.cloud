from indicator import models
from rest_framework import serializers


class IndicatorTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Indicator
        fields = (
            'id',
            'description',
            'friendly_label',
            'type_data',
            'deprivation_type',
            'category'
        )


class IndicatorSerializer(serializers.ModelSerializer):
    indicator = IndicatorTypeSerializer()

    class Meta:
        model = models.IndicatorData
        fields = (
            'indicator',
            'year',
            'value',
            'selection_type'
        )
