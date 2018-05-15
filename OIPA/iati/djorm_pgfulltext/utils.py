import psycopg2

from django.db import connections
from django.utils.encoding import force_text

def adapt(text):
    a = psycopg2.extensions.adapt(force_text(text))
    a.prepare(connections['default'].cursor().connection)
    return a
