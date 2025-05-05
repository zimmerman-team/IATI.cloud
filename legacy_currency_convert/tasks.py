import json

from celery import shared_task
from django.conf import settings

from legacy_currency_convert.models import MonthlyAverage


@shared_task
def update_exchange_rates():
    """
    This task updates all of the currency exchange rates in the local
    database and updates the exchange rates dump.
    """
    from legacy_currency_convert.imf_rate_parser import RateParser
    r = RateParser()
    r.update_rates(force=False)
    _dump()


@shared_task
def dump_exchange_rates():
    _dump()


def _dump():
    """
    Dump the exchange rates to a JSON file.
    """
    avgs = MonthlyAverage.objects.all()
    avgs_list = []
    for avg in avgs:
        avg_dict = {
            'year': avg.year,
            'month': avg.month,
            'currency_id': avg.currency.code,
            'value': float(avg.value),
        }
        avgs_list.append(avg_dict)

    with open(f'{settings.BASE_DIR}/direct_indexing/data_sources/currency_monthlyaverage.json', 'w') as f:
        json.dump(avgs_list, f)
