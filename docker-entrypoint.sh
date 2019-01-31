#!/bin/sh
# wait-for-postgres.sh

################################################################################
# An entrypoint script for OIPA which waits for the database to start, then    #
# runs migrations and then executes given startup command for a Docker service #
################################################################################

set -e

cmd="$@"

#Wait for database:

#FIXME: this is quite sensitive and at some cases fails, because it is very
#difficult to determine when database is at 'ready' state. Especially when db
#already exists. A workaround is to remove postgis image and run
#'docker-compose up' again. TODO: wait for open port?:
# https://stackoverflow.com/a/27601038/2942981

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

#If Supervisor process (for parsing) isn't started, start it:

#pgrep -f -x "python ./OIPA/manage.py supervisor"
#FIXME: start this as a separate service in docker-compose:
python3.6 /app/src/OIPA/manage.py supervisor -d

# Start dev server:
>&2 echo "Postgres is up - executing command . . ."
exec $cmd
