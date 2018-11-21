import os

import django

from iati.transaction.models import TransactionProvider, TransactionReceiver

os.environ["DJANGO_SETTINGS_MODULE"] = "OIPA.settings"
django.setup()


with open('supergraph.dot', 'w', buffering=20*(1024**2)) as output:
    output.write("digraph IATI{\n")

    for t in TransactionProvider.objects.all().filter(
        provider_activity__isnull=False
    ).select_related('transaction'):
        output.write(
            "\t\"{provider}\" -> \"{receiver}\" [color = red, label={type}];\n".format(  # NOQA: E501
                provider=t.provider_activity_id,
                receiver=t.transaction.activity_id,
                type=t.transaction.transaction_type.code,
            )
        )

    for t in TransactionReceiver.objects.all().filter(
        receiver_activity__isnull=False
    ).select_related('transaction'):
        output.write("\t\"{provider}\" -> \"{receiver}\" [color = blue, label={type}];\n".format(  # NOQA: E501
                provider=t.transaction.activity_id,
                receiver=t.receiver_activity_id,
                type=t.transaction.transaction_type.code,
            )
        )

    output.write('}\n')
