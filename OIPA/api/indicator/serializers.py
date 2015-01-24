from indicator import models
from rest_framework import serializers


class IndicatorDataValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IndicatorDataValue
        fields = ('year', 'value')


class IndicatorSerializer(serializers.ModelSerializer):
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


class IndicatorDataSerializer(serializers.ModelSerializer):
    indicator = IndicatorSerializer()
    values = IndicatorDataValueSerializer(many=True)

    class Meta:
        model = models.IndicatorData
        fields = (
            'indicator',
            'values',
            'selection_type'
        )
