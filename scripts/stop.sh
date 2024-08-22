#!/bin/bash

# Help
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
  echo "Used to stop services running through docker. Optionally specify service names."
  echo ""
  echo "Usage: bash $0 [service name (optional) (up to 9 service names, and -d)]"
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
sudo docker compose down $I1 $I2 $I3 $I4 $I5 $I6 $I7 $I8 $I9 $I10

echo "Stop script is done."
