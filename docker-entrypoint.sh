#!/bin/sh
# wait-for-postgres.sh

################################################################################
# An entrypoint script for OIPA which waits for the database to start, then    #
# runs migrations and then executes given startup command for a Docker service #
################################################################################

set -e

cmd="$@"

#Wait for database to be ready:
until PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

#We need this when Docker containers are *resumed*, because stuff happens too
#quickly (when database container is already built) and the above psql check
#can not even detect it:
>&2 echo "Caution sleeping for 5 secs . . ."
sleep 5

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
>&2 echo "\n\n\n*** Database is up - executing Docker container entrypoint (startup) command ***\n\n\n"
exec $cmd
