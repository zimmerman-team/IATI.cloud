#!/bin/bash
set -e

# run migrations
/app/src/OIPA/manage.py migrate --noinput

# generate static files
/app/src/OIPA/manage.py collectstatic --noinput

# run Django as a wsgi process
/app/src/bin/wait-for-postgres.sh -- /venv/bin/uwsgi \
    --chdir=/app/src/OIPA \
    --module=OIPA.wsgi:application \
    --env DJANGO_SETTINGS_MODULE=OIPA.settings \
    --master --pidfile=/tmp/uwsgi.pid \
    --http 0.0.0.0:8000 \
    --buffer-size 32768 \
    --processes=5 \
    --uid=1000 --gid=1000 \
    --vacuum \
    --home=/venv
