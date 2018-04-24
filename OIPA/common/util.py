from __future__ import division

import threading
import unicodedata
from functools import reduce

import psycopg2
from django.db import connection
from django.db.models import Q
from django.utils.text import force_text


def get_or_none(model, *args, **kwargs):
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None


def print_progress(progress):
    """progress: object with offset and count"""
    print("Progress: {offset}/{count}: {perc}%".format(
        offset=progress['offset'],
        count=progress['count'],
        perc=round(round(progress['offset'] / progress['count'], 4) * 100, 2),
    ))


def setInterval(func, sec):
    def func_wrapper():
        setInterval(func, sec)
        func()

    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


def difference(list1, list2):
    set(list2)
    return [a for a in list1 if a not in list2]


def combine_filters(filters):
    ### combine Q objects ###
    if len(filters) == 1:
        return filters[0]
    return reduce(lambda q1, q2: q1 | q2, filters, Q())


def adapt(text):
    a = psycopg2.extensions.adapt(force_text(text))
    a.prepare(connection.connection)
    return a


def findnth_occurence_in_string(haystack, needle, n):
    """
    returns the index of the nth occurence of the needle in the haystack
    """
    parts = haystack.split(needle, n + 1)
    if len(parts) <= n + 1:
        return -1
    return len(haystack) - len(parts[-1]) - len(needle)


def normalise_unicode_string(any_str):
    """
    Cleanup up a string.
    :param any_str: Any string
    :return: Unicode string
    """
    if str is not None:
        if isinstance(any_str, unicode):
            any_str = unicodedata.normalize("NFKD", any_str)
    return any_str
