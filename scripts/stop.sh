#!/bin/bash

# Import utility functions
source ./scripts/util.sh

helper $0 $1 \
  "$0
Used to stop services running through docker.
Optionally specify service names.

Always run from the root directory of the IATI.cloud project.
Uses with sudo access.

Usage:
  $0 [--help] [-a] [-ic] [...service names...]

General options:
  -h [--help]         show this help message
  -a [--all]          start all services (detached)
  -ic [--iaticloud]   start IATI.cloud services (detached):
                      iaticloud, celeryworker, celeryaidaworker,
                      celeryrevokeworker, celeryscheduler, celeryflower

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

# Check if the first argument is "all" or "ic"
if [ "$1" = "--all" ] || [ "$1" = "-a" ] || [ -z "$1" ]; then
  print_status "Stopping all services..."
  sudo docker compose down
  print_status "Stopping all services is done."
  exit 0
elif [ "$1" = "-ic" ] || [ "$1" = "--iaticloud" ]; then
  print_status "Stopping IATI.cloud services (iaticloud celeryworker celeryaidaworker celeryrevokeworker celeryscheduler celeryflower)..."
  sudo docker stop iaticloud celeryworker celeryaidaworker celeryrevokeworker celeryscheduler celeryflower
  print_status "Stopping IATI.cloud services is done."
  exit 0
fi

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
print_status "Stopping services: $I1 $I2 $I3 $I4 $I5 $I6 $I7 $I8 $I9 $I10"
sudo docker stop $I1 $I2 $I3 $I4 $I5 $I6 $I7 $I8 $I9 $I10

print_status "Stop script is done."
