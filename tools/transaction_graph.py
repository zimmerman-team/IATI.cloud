import os, django
os.environ["DJANGO_SETTINGS_MODULE"] = "OIPA.settings"
django.setup()

from iati.models import Activity
from iati.transaction.models import Transaction, TransactionProvider, TransactionReceiver

with open('supergraph.dot', 'w', buffering=20*(1024**2)) as output:
    output.write("digraph IATI{\n")

    for t in TransactionProvider.objects.all().filter(provider_activity__isnull=False).select_related('transaction'):
        output.write("\t\"{provider}\" -> \"{receiver}\" [color = red, label={type}];\n".format(
            provider=t.provider_activity_id,
            receiver=t.transaction.activity_id,
            type=t.transaction.transaction_type.code,
        ))


    for t in TransactionReceiver.objects.all().filter(receiver_activity__isnull=False).select_related('transaction'):
        output.write("\t\"{provider}\" -> \"{receiver}\" [color = blue, label={type}];\n".format(
            provider=t.transaction.activity_id,
            receiver=t.receiver_activity_id,
            type=t.transaction.transaction_type.code,
        ))

    # for t in TransactionReceiver.objects.all().filter(receiver_activity__isnull=True).select_related('transaction'):
    #     a = t.narratives.all()
    #     if (len(a) > 0):
    #         output.write("\t\"{provider}\" -> \"{receiver_org}\" [color = yellow, label={type}];\n".format(
    #             provider=t.transaction.activity_id,
    #             receiver_org=a[0].content,
    #             type=t.transaction.transaction_type.code,
    #         ))


    output.write('}\n')
