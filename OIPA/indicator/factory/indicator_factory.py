import indicator
from factory.django import DjangoModelFactory


class NoDatabaseFactory(DjangoModelFactory):
    @classmethod
    def _setup_next_sequence(cls):
        return 0


class IndicatorDataValueFactory(NoDatabaseFactory):
    class Meta:
        model = indicator.models.IndicatorDataValue

    value = 100
    year = 2000


class IndicatorFactory(NoDatabaseFactory):
    class Meta:
        model = indicator.models.Indicator

    description = 'some indicator'
    friendly_label = 'friendly label'
    type_data = 'n'


class IndicatorDataFactory(NoDatabaseFactory):
    class Meta:
        model = indicator.models.IndicatorData
