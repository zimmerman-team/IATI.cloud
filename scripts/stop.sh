#!/bin/bash

# Help
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
  echo "Used to stop services running through docker. Optionally specify service names."
  echo ""
  echo "Usage: bash $0 [service name (optional) (up to 9 service names, and -d)]"
  exit 0
fi

# Check if the first argument is "all" or "ic"
if [ "$1" = "all" ]; then
  echo "Stopping all services..."
  sudo docker compose down
  echo "Stopping all services is done."
  exit 0
elif [ "$1" = "ic" ]; then
  echo "Stopping IATI.cloud services (iaticloud celeryworker celeryaidaworker celeryrevokeworker celeryscheduler celeryflower)..."
  sudo docker compose down iaticloud celeryworker celeryaidaworker celeryrevokeworker celeryscheduler celeryflower
  echo "Stopping IATI.cloud services is done."
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
echo "Stopping services: $I1 $I2 $I3 $I4 $I5 $I6 $I7 $I8 $I9 $I10"
sudo docker compose down $I1 $I2 $I3 $I4 $I5 $I6 $I7 $I8 $I9 $I10

echo "Stop script is done."
