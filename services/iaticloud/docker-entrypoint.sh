#!/bin/bash
. /app/.env
# Wait for postgres to be up
echo "---IATICLOUD DOCKER ENTRYPOINT---"
echo "Startup sleep timer..."
sleep 15

# # Set up django's migrations
echo "Running django migrations..."
python manage.py makemigrations
RES=`python manage.py migrate`
if [[ "$RES" == *"No migrations to apply"* ]]; then
  echo "No changes detected, returning to main docker process..."
  exec "$@"
fi

# # First time setup
echo "Collecting static files..."
python manage.py collectstatic --noinput

# # Preload the initial data
python manage.py loaddata services/iaticloud/data_preload/legacy_currency_convert_dump.json
# # Set up an initial superuser with the password provided in $DJANGO_SUPERUSER_PASSWORD in .env
echo "Creating superuser..."
python manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USERNAME --email $DJANGO_SUPERUSER_EMAIL

$@
