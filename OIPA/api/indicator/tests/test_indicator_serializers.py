from api.indicator import serializers
from indicator.factory import indicator_factory


class TestIndicatorDataValueSerializer:
    indicator_value = indicator_factory.IndicatorDataValueFactory.build(
        year=2015,
        value=1000)
    serializer = serializers.IndicatorDataValueSerializer(indicator_value)
    field_msg = """
                'IndicatorDataValue.{0}' should be serialized to a field
                called '{1}'
                """

    def test_year_field(self):
        assert self.serializer.data['year'] == self.indicator_value.year,\
            self.field_msg.format('year', 'year')

    def test_value_field(self):
        assert self.serializer.data['value'] == self.indicator_value.value,\
            self.field_msg.format('value', 'value')


class TestIndicatorSerializer:
    indicator = indicator_factory.IndicatorFactory.build(
        id='literacy_rate_women_rural',
        description='UNHABITAT_UNHABITAT_DHS',
        friendly_label='Literacy rate by shelter deprivation (Women) - Rural',
        type_data='p',
        deprivation_type='blam',
        category='Slum dwellers')
    serializer = serializers.IndicatorSerializer(indicator)
    field_msg = """
                'Indicator.{0}' should be serialized to a field called '{1}'
                """

    def test_id_field(self):
        assert self.serializer.data['id'] == self.indicator.id,\
            self.field_msg.format('id', 'id')

    def test_description_field(self):
        serializer_description = self.serializer.data['description']
        assert serializer_description == self.indicator.description,\
            self.field_msg.format('description', 'description')

    def test_friendly_label_field(self):
        serializer_friendly_label = self.serializer.data['friendly_label']
        assert serializer_friendly_label == self.indicator.friendly_label,\
            self.field_msg.format('friendly_label', 'friendly_label')

    def test_type_data_field(self):
        serializer_type_data = self.serializer.data['type_data']
        assert serializer_type_data == self.indicator.type_data,\
            self.field_msg.format('type_data', 'type_data')

    def test_deprivation_type_field(self):
        deprivation_type = self.serializer.data['deprivation_type']
        assert deprivation_type == self.indicator.deprivation_type,\
            self.field_msg.format('deprivation_type', 'deprivation_type')

    def test_category_field(self):
        assert self.serializer.data['category'] == self.indicator.category,\
            self.field_msg.format('category', 'category')


class TestIndicatorDataSerializer:
    indicator_data = indicator_factory.IndicatorDataFactory.build(
        selection_type='test')
    serializer = serializers.IndicatorDataSerializer(indicator_data)

    def test_selection_type_field(self):
        selection_type = self.serializer.data['selection_type']
        assert selection_type == self.indicator_data.selection_type,\
            """
            'IndicatorData.selection_type' should be serialized to a field
            called 'selection_type'
            """

    def test_indicator_field(self):
        indicator_field = self.serializer.fields['indicator']
        assert type(indicator_field) == serializers.IndicatorSerializer,\
            """
            IndicatorDataSerializer should have a field called 'indicator'
            of the type 'IndicatorSerializer'
            """

    def test_values_field(self):
        values = self.serializer.fields['values']
        assert type(values.child) == serializers.IndicatorDataValueSerializer,\
            """
            IndivatorDataSerializer should have a field called 'values' that
            contains a list of 'IndicatorDataValueSerializer'
            """
