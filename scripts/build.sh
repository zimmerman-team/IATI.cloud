#!/bin/bash

# Import utility functions
source ./scripts/util.sh

helper $0 $1 \
  "$0
Used to (re)build services running through docker.
Optionally specify service names.

Always run from the root directory of the IATI.cloud project.
Uses with sudo access.

Usage:
    $0 [--help] [...service names...]

General options:
  -h [--help]         show this help message

Docker service options:
  database            docker service: IATI.cloud postgres database
  rabbitmq            docker service: rabbitmq
  mongo               docker service: IATI.cloud mongo database
  solr                docker service: IATI.cloud solr database
  iaticloud           docker service: IATI.cloud main service
  celeryworker        docker service: IATI.cloud general celery workers
  celeryaidaworker    docker service: IATI.cloud AIDA specific celery workers
  celeryrevokeworker  docker service: IATI.cloud revoke specific celery workers
  celeryscheduler     docker service: IATI.cloud scheduler celery beat
  celeryflower        docker service: IATI.cloud celery flower
"

# Start
# Get additional arguments (service names)
I1="$1"
I2="$2"
I3="$3"
I4="$4"
I5="$5"
I6="$6"
I7="$7"
I8="$8"
I9="$9"
I10="$10"

sudo docker compose build $I1 $I2 $I3 $I4 $I5 $I6 $I7 $I8 $I9 $I10

echo "Build script is done. You can now start the services using the './scripts/start.sh $MODE' script."
