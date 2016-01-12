from __future__ import division
import psycopg2


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

def adapt(text):
    a = psycopg2.extensions.adapt(force_text(text))
    a.prepare(connection.connection)
    return a
