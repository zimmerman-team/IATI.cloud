from __future__ import division
import psycopg2

from django.db.models import Q

from django.db import connection
from django.utils.text import force_text
import threading


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
    if len(filters) == 1: return filters[0]
    return reduce(lambda q1,q2: q1 | q2, filters, Q())


def adapt(text):
    a = psycopg2.extensions.adapt(force_text(text))
    a.prepare(connection.connection)
    return a
