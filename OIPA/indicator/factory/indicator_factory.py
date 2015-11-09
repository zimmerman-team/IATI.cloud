from indicator.models import IndicatorDataValue
from indicator.models import Indicator
from indicator.models import IndicatorData
from indicator.models import CsvUploadLog

from factory.django import DjangoModelFactory


class NoDatabaseFactory(DjangoModelFactory):
    @classmethod
    def _setup_next_sequence(cls):
        return 0


class IndicatorDataValueFactory(NoDatabaseFactory):
    class Meta:
        model = IndicatorDataValue

    value = 100
    year = 2000


class IndicatorFactory(NoDatabaseFactory):
    class Meta:
        model = Indicator

    id ='health_indicator'
    description = 'some health indicator'
    friendly_label = 'friendly label'
    type_data = 'n'
    category = 'health'


class IndicatorDataFactory(NoDatabaseFactory):
    class Meta:
        model = IndicatorData


class CsvUploadLogFactory(NoDatabaseFactory):
    class Meta:
        model = CsvUploadLog