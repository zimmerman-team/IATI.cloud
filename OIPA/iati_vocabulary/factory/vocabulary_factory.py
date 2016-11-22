from iati.models import RegionVocabulary
from iati.models import GeographicVocabulary

from iati_codelists import models as codelist_models
from iati_vocabulary import models as vocabulary_models

from factory.django import DjangoModelFactory


class NoDatabaseFactory(DjangoModelFactory):
    @classmethod
    def _setup_next_sequence(cls):
        return 0


class GetOrCreateMetaMixin():
    django_get_or_create = ('code',)


class SectorVocabularyFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = vocabulary_models.SectorVocabulary

    code = "1"
    name = "OECD DAC CRS (5 digit)"


class BudgetIdentifierVocabularyFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = codelist_models.BudgetIdentifierVocabulary

    code = "1"
    name = "IATI"


class PolicyMarkerVocabularyFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = vocabulary_models.PolicyMarkerVocabulary

    code = "1"
    name = "OECD DAC CRS"


class RegionVocabularyFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = RegionVocabulary

    code = "1"
    name = 'test vocabulary'


class GeographicVocabularyFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = GeographicVocabulary

    code = 'A1'
    name = 'Global Admininistrative Unit Layers'
    description = 'description'


class HumanitarianScopeVocabularyFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = vocabulary_models.HumanitarianScopeVocabulary

    code = '1-1'
    name = 'UN OCHA FTS'
    description = 'description'


class IndicatorVocabularyFactory(NoDatabaseFactory):
    class Meta(GetOrCreateMetaMixin):
        model = vocabulary_models.IndicatorVocabulary

    code = '1'
    name = 'WHO Registry'
    description = 'description'
