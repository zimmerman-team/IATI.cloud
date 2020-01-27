from api.iati.references import TransactionReference as ElementReference
from solr.references import ConvertElementReference
from solr.transaction.serializers import TransactionSerializer


class TransactionReference(ConvertElementReference, ElementReference):

    def __init__(self, transaction=None):
        data = TransactionSerializer(
            instance=transaction,
            fields=[
                'id',
                'activity_id',
                'ref',
                'humanitarian',
                'transaction_type',
                'transaction_date',
                'value',
                'value_date',
                'currency',
                'description',
                'currency',
                'description',
                'provider_organisation',
                'receiver_organisation',
                'disbursement_channel',
                'sector',
                'recipient_country',
                'recipient_region',
                'flow_type',
                'finance_type',
                'aid_type',
                'tied_status',
                'sectors',
                'iati_identifier',
                'recipient_countries',
                'recipient_regions'
            ]
        ).data

        super().__init__(parent_element=None, data=data)
