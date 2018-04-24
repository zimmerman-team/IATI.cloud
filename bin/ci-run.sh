#!/bin/sh

set -x -o errexit

COVERAGE_FILE=/tmp/coverage coverage run --source=. --omit=*__init__*,*data_backup* manage.py test --nomigrations --verbosity 3
coveralls -d /tmp/coverage
