from datetime import date
from factory import SubFactory
from iati.transaction.models import Transaction, TransactionSector, TransactionRecipientCountry, TransactionRecipientRegion
from iati.transaction.models import TransactionType

from iati.factory.iati_factory import NoDatabaseFactory
from iati.factory.iati_factory import ActivityFactory
from iati.factory.iati_factory import SectorFactory, SectorVocabularyFactory, RegionFactory, RegionVocabularyFactory, CountryFactory

from iati_codelists.factory.codelist_factory import CurrencyFactory


class TransactionTypeFactory(NoDatabaseFactory):
    code = "1"
    name = "Incoming Funds"
    description = ""

    class Meta:
        model = TransactionType

class TransactionProviderFactory(NoDatabaseFactory):
    ref = "some-ref"
    normalized_ref = "some_ref"
    provider_activity = SubFactory(ActivityFactory)
    provider_activity_ref = "IATI-0001"

class TransactionReceiverFactory(NoDatabaseFactory):
    ref = "some-ref"
    normalized_ref = "some_ref"
    receiver_activity = SubFactory(ActivityFactory)
    receiver_activity_ref = "IATI-0001"

class TransactionFactory(NoDatabaseFactory):

    activity = SubFactory(ActivityFactory)

    transaction_type = SubFactory(TransactionTypeFactory, code=1)
    transaction_date = date.today()

    value = 200
    value_string = "200"
    value_date = date.today()
    currency = SubFactory(CurrencyFactory)


    class Meta:
        model = Transaction

class TransactionSectorFactory(NoDatabaseFactory):
    class Meta:
        model = TransactionSector

    transaction = SubFactory(TransactionFactory)
    sector = SubFactory(SectorFactory)
    vocabulary = SubFactory(SectorVocabularyFactory)

    percentage = 100
    xdr_value = 10000
    reported_on_transaction = False

class TransactionRecipientCountryFactory(NoDatabaseFactory):
    class Meta:
        model = TransactionRecipientCountry

    transaction = SubFactory(TransactionFactory)
    country = SubFactory(CountryFactory)

    percentage = 100
    xdr_value = 10000
    reported_on_transaction = False

class TransactionRecipientRegionFactory(NoDatabaseFactory):
    class Meta:
        model = TransactionRecipientRegion

    transaction = SubFactory(TransactionFactory)
    region = SubFactory(RegionFactory)

    percentage = 100
    xdr_value = 10000
    reported_on_transaction = False

