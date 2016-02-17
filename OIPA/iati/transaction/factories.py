from datetime import date
from factory import SubFactory
from iati.transaction.models import Transaction
from iati.transaction.models import TransactionType
from iati.factory.iati_factory import NoDatabaseFactory
from iati.factory.iati_factory import ActivityFactory

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
