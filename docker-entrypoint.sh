#!/bin/sh
# wait-for-postgres.sh

################################################################################
# An entrypoint script for OIPA which waits for the database to start, then    #
# runs migrations and then executes given startup command for a Docker service #
################################################################################

set -e

cmd="$@"

#Wait for database:

#XXX: this is quite sensitive and at some cases might fail, because it is very
#difficult to determine when database is at 'ready' state. Try to play around
#with 'sleep' settings here.
until PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

#Run migrations:
>&2 echo "Running migrations . . ."

python3.6 /app/src/OIPA/manage.py migrate

#Create superuser:
>&2 echo "Creating superuser . . ."

python3.6 /app/src/OIPA/manage.py shell -c \
"from django.contrib.auth.models import User; \
User.objects.create_superuser('$SUPERUSER_USERNAME', '$SUPERUSER_EMAIL', '$SUPERUSER_PASSWORD') \
if not User.objects.filter(username='$SUPERUSER_USERNAME').exists() \
else 'Superuser already exists . . .'"

# Start dev server:
>&2 echo "Postgres is up - executing command . . ."
exec $cmd
