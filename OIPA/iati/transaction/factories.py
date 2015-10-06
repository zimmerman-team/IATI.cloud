from datetime import date
from factory import SubFactory
from iati.transaction.models import Transaction
from iati.transaction.models import TransactionType
from iati.factory.iati_factory import NoDatabaseFactory
from iati.factory.iati_factory import ActivityFactory


class TransactionTypeFactory(NoDatabaseFactory):
    code = "tes-type"
    name = "test transaction type"
    description = ""

    class Meta:
        model = TransactionType


class TransactionFactory(NoDatabaseFactory):
    id = 1
    activity = SubFactory(ActivityFactory)
    transaction_date = date.today()
    transaction_type = SubFactory(TransactionTypeFactory, code=1)

    class Meta:
        model = Transaction
