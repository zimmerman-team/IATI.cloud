#!/bin/bash
# Waits for Postgres to be available and runs a command
# wait-for-postgres.sh

set -e

cmd="$@"

until PGPASSWORD=${OIPA_DB_PASSWORD} psql -h "${OIPA_DB_HOST}" -U "${OIPA_DB_USER}" ${OIPA_DB_NAME} -c '\l' > /dev/null; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"
exec $cmd
