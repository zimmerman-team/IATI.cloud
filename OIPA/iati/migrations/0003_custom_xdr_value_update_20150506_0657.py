# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from iati.currency_converter import convert


def update_xdr_values(apps, schema_editor):
    Transaction = apps.get_model('iati', 'Transaction')
    transactions = Transaction.objects.all()
    count = transactions.count()
    print '\n updating transactions:'
    index = 0
    for transaction in transactions:
        if index % 1000 == 0:
            print '{0} - {1} done'.format(index, count)
        transaction.xdr_value = convert.to_xdr(
            transaction.currency,
            transaction.value_date,
            transaction.value)
        transaction.save()
        index = index + 1
    print '{0} of {1} done'.format(index, count)


class Migration(migrations.Migration):

    dependencies = [
        ('iati', '0002_transaction_xdr_value'),
    ]

    operations = [
        migrations.RunPython(update_xdr_values, lambda x, y: None)
    ]
